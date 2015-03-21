from collections import OrderedDict
import os.path

from django.conf import settings
from django.db import connections

from ..exceptions import ImproperlyConfigured
from ..types import DateTime, Date
from .configurations import IndexerConfiguration, \
    SearchdConfiguration, \
    SourceConfiguration, \
    IndexConfiguration
from . import constants


def add_source_conf_param(source_conf, key, value):
    """
    Adds a {key: value} to source_conf taking into account if
    key is a multi_valued_parameter or single_valued_parameter.
    """
    if key in constants.source_multi_valued_parameters:
        if key not in source_conf:
            source_conf[key] = []
        source_conf[key].append(value)
    elif key in constants.source_single_valued_parameters:
        source_conf[key] = value
    else:
        raise ImproperlyConfigured('Invalid parameter "%s" in source '
                                   'configuration' % key)
    return source_conf


SPHINX_TO_DJANGO_MAP = {'user': 'sql_user',
                        'passwd': 'sql_pass', 'password': 'sql_pass',
                        'db': 'sql_db', 'database': 'sql_db',
                        'port': 'sql_port',
                        'host': 'sql_host',
                        'unix_socket': 'sql_sock'
                        }

DJANGO_TO_SPHINX_VENDOR = {'postgresql': 'pgsql',
                           'mysql': 'mysql'}

DEFAULT_INDEXER_PARAMS = {}

DEFAULT_SOURCE_PARAMS = {'sql_host': 'localhost',
                         'sql_pass': '',
                         }

DEFAULT_SEARCHD_PARAMS = {'listen': '9306:mysql41',
                          }

DEFAULT_INDEX_PARAMS = {'type': 'plain'}


class Configurator(object):
    """
    The main configurator.

    Uses the settings dictionary ``INDEXES``.
    """
    def __init__(self):
        if not hasattr(settings, 'INDEXES'):
            raise ImproperlyConfigured('Django-SphinxQL requires '
                                       'settings.INDEXES')

        self.sphinx_path = settings.INDEXES.get('sphinx_path')
        self.path = settings.INDEXES['path']
        self.sphinx_file = os.path.join(self.sphinx_path, 'sphinx.conf')

        self.vendor = ''

        # index
        self.index_params = DEFAULT_INDEX_PARAMS
        self.index_params.update(settings.INDEXES.get('index_params', {}))

        # source
        self.source_params = DEFAULT_SOURCE_PARAMS
        self.source_params.update(settings.INDEXES.get('source_params', {}))

        # searchd
        searchd_params = DEFAULT_SEARCHD_PARAMS
        searchd_params['pid_file'] = os.path.join(self.sphinx_path, 'searchd.pid')
        searchd_params.update(settings.INDEXES.get('searchd_params', {}))

        # indexer
        indexer_params = DEFAULT_INDEXER_PARAMS
        indexer_params.update(settings.INDEXES.get('indexer_params', {}))

        self.indexer_conf = IndexerConfiguration(indexer_params)
        self.searchd_conf = SearchdConfiguration(searchd_params)

        self.indexes = OrderedDict()
        self.indexes_confs = []
        self.sources_confs = []

    def register(self, index):
        """
        Registers an index to the configurator and outputs the updated
        sphinx.conf file.
        """
        meta = getattr(index.Meta.model, '_meta', None)
        assert meta is not None

        assert index not in self.indexes.values()
        self.indexes[index.build_name()] = index

        # build the source and index config.
        source_conf = self._conf_source_from_index(index)
        self.sources_confs.append(source_conf)

        index_conf = self._conf_index_from_index(index, source_conf.name)
        self.indexes_confs.append(index_conf)

        # since we don't know when the last index is registered,
        # we output on every registration.
        # todo: in Django 1.7 this could done on app.ready()
        self.output()

    def _conf_source_from_index(self, index):
        """
        Maps an ``Index`` into a Sphinx source configuration.
        """
        source_attrs = {}
        source_attrs.update(self.source_params)
        source_attrs.update(getattr(index.Meta, 'source_params', {}))

        if hasattr(index.Meta, 'query'):
            query = index.Meta.query
        else:
            query = index.Meta.model.objects.all()

        ### select type from backend
        if connections[query.db].vendor not in DJANGO_TO_SPHINX_VENDOR:
            raise ImproperlyConfigured('Django-SphinxQL currently only supports '
                                       'mysql and postgresql backends')
        self.vendor = DJANGO_TO_SPHINX_VENDOR[connections[query.db].vendor]

        source_attrs = add_source_conf_param(source_attrs, 'type', self.vendor)

        if self.vendor == 'mysql':
            source_attrs = add_source_conf_param(source_attrs, 'sql_query_pre',
                                                 'SET CHARACTER_SET_RESULTS=utf8')

        ### build connection parameters from Django connection parameters
        connection_params = connections[query.db].get_connection_params()
        for key in connection_params:
            if key in SPHINX_TO_DJANGO_MAP:
                value = SPHINX_TO_DJANGO_MAP[key]
                source_attrs = add_source_conf_param(source_attrs,
                                                     value,
                                                     connection_params[key])

        ### create parameters for fields and attributes
        for field in index.Meta.fields:
            sphinx_field_name = field._sphinx_field_name

            source_attrs = add_source_conf_param(source_attrs,
                                                 sphinx_field_name,
                                                 field.name)

        if hasattr(index.Meta, 'range_step'):
            # see http://sphinxsearch.com/docs/current.html#ranged-queries
            range_step = int(index.Meta.range_step)

            source_attrs = add_source_conf_param(
                source_attrs, 'sql_query_range',
                'SELECT MIN(id),MAX(id) FROM %s' % index.Meta.model._meta.db_table)
            source_attrs = add_source_conf_param(
                source_attrs, 'sql_range_step', range_step)
            query = query.extra(where=['id>=$start AND id<=$end'])

        ### add the query
        source_attrs = add_source_conf_param(
            source_attrs,
            'sql_query',
            self._build_query(index, query, self.vendor))

        return SourceConfiguration(index.build_name(), source_attrs)

    @staticmethod
    def _build_query(index, query, vendor):
        """
        Returns a SQL query built according to the fields selected
        """
        def qn(value):
            if vendor == 'mysql':
                return '`%s`' % value
            else:
                return '"%s"' % value

        # Prepare the query Sphinx will use: select only the fields we use.
        # Because fields in Meta are ordered as Django fields, this will
        # map them correctly
        select = OrderedDict(id='id')
        for field in index.Meta.fields:
            column_name = qn(index.get_model_field(field.model_attr))
            alias = qn(field.name)
            sql = "%s"
            if vendor == 'mysql':
                if field.type() in (DateTime, Date):
                    # for dates, we need the timestamp.
                    # To ensure we get the correct timestamp
                    # (i.e. same as Django uses),
                    # in mysql we convert it to UTC.
                    sql = "UNIX_TIMESTAMP(CONVERT_TZ(" \
                          "%s, " \
                          "'+00:00', " \
                          "@@session.time_zone))"
            if vendor == 'pgsql':
                if field.type() is DateTime:
                    sql = "EXTRACT(EPOCH FROM %s AT TIME ZONE '%s')" % \
                          ('%s', settings.TIME_ZONE)
                elif field.type() is Date:
                    sql = "EXTRACT(EPOCH FROM %s)"
            select["%s" % alias] = sql % column_name

        query = query.only('id').extra(select=select)

        # transform into SQL
        return str(query.query)

    def _conf_index_from_index(self, index, source_name):
        """
        Maps a ``Index`` into a Sphinx index configuration.
        """
        index_params = {
            'source': source_name,
            'path': os.path.join(self.path, source_name)
        }
        index_params.update(self.index_params)
        index_params.update(getattr(index.Meta, 'index_params', {}))

        return IndexConfiguration(index.build_name(), index_params)

    def reconfigure(self):
        """
        This reconfigures the existing indexes.

        this is to implement an hack for tests: Django does not support apps using
        its connections on loading for tests; see warning in
        https://docs.djangoproject.com/en/1.7/ref/applications/#django.apps.AppConfig.ready
        """
        self.sources_confs.clear()
        self.indexes_confs.clear()
        for index in self.indexes.values():
            source_conf = self._conf_source_from_index(index)
            index_conf = self._conf_index_from_index(index, source_conf.name)
            self.sources_confs.append(source_conf)
            self.indexes_confs.append(index_conf)

        self.output()

    def output(self):
        """
        Outputs the configuration file `sphinx.conf`.
        """
        string = "# WARNING! This file was automatically generated: do not " \
                 "modify it.\n\n"

        # output all source and indexes
        for i in range(len(self.indexes)):
            string += self.sources_confs[i].format_output()
            string += '\n'
            string += self.indexes_confs[i].format_output()

        # output indexer and searchd
        string += self.indexer_conf.format_output()
        string += self.searchd_conf.format_output()

        with open(self.sphinx_file, 'w') as conf_file:
            conf_file.write(string)
