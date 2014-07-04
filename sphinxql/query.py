from collections import OrderedDict

from django.db.models import query

from .core.query import Query
from .core import base
from .core import lookups
from sphinxql.exceptions import NotSupportedError
from .types import Bool, String
from .sql import Match, And, Neg, C, Column, All, Count


LOOKUP_SEPARATOR = '__'


def parse_lookup(lhs, rhs):
    assert lhs
    parts = lhs.split(LOOKUP_SEPARATOR)

    if len(parts) > 2:
        raise NotImplementedError('Currently Django-SphinxQL only accepts'
                                  'lookups having up to 1 \'__\'.')
    rhs = base.convert(rhs)

    if len(parts) == 1:
        parts.append('eq')

    column = C(parts[0])
    lookup = parts[1]

    try:
        operation = lookups.LOOKUPS[lookup]
    except KeyError:
        raise KeyError('Lookup \'{0}\' not valid. '
                       'Check documentation on available lookups.'
                       .format(parts[1]))

    return operation(column, rhs)


class QuerySet(object):

    def __init__(self, index):
        self._index = index
        self.query = Query()
        self.query.fromm.append(index)

        # Sphinx: there can be only one match per query.
        # This is a global constraint on queries
        # We keep it here.
        self._match = ''

        self._result_cache = None
        self._fetch_cache = None

        self._set_default_fields(self.query)

    def _fetch_raw(self):
        """
        Fetches by hitting Sphinx
        """
        if self._fetch_cache is not None:
            return self._fetch_cache

        self._fetch_cache = list(self._get_query())
        return self._fetch_cache

    def _get_query(self):
        """
        Returns a copy of the query exactly prior to hit db.
        """
        clone = self.query.clone()
        if self._match:
            clone.where = self._add_condition(clone.where, Match(String(self._match)))
        return clone

    def _parsed_results(self):
        """
        Hits Sphinx and parses the results into indexes instances.
        """
        for result in self._fetch_raw():
            instance = self._index()

            setattr(instance, 'id', result[0])
            i = 1
            for field in self._index.Meta.fields:
                setattr(instance, field.name, field.type().to_python(result[i]))
                i += 1

            yield instance

    def __iter__(self):
        return iter(self._parsed_results())

    def __len__(self):
        if self._fetch_cache is not None:
            return len(self._fetch_cache)
        return self.count()

    def __getitem__(self, item):
        if not isinstance(item, (slice, int)):
            raise TypeError
        if isinstance(item, slice):
            if item.stop is None:
                raise NotSupportedError('Sphinx does not support unbounded slicing.')

        if isinstance(item, slice):
            offset = item.start or 0
            count = item.stop - offset

            clone = self.clone()
            clone.query.limit = (offset, count)
            return list(clone)
        else:
            offset = item
            count = 1
            clone = self.clone()
            clone.query.limit = (offset, count)
            return list(clone)[0]

    def all(self):
        return self

    def count(self):
        q = self._get_query()
        q.select.clear()
        q.select.append(Count(All()))

        result = list(q)
        if result:
            # first row, second entry (first entry is row's `id`)
            return result[0][1]
        else:
            return 0

    def filter(self, *conditions, **lookups):
        clone = self.clone()

        conditions = list(conditions)
        for lookup in lookups:
            condition = parse_lookup(lookup, lookups[lookup])
            conditions.append(condition)

        for condition in conditions:
            assert isinstance(condition, base.SQLExpression)
            condition = condition.resolve_columns(self._index)
            assert condition.type() == Bool
            clone.query.where = self._add_condition(clone.query.where, condition)

        return clone

    def search(self, extended_query):
        assert isinstance(extended_query, str)
        # concatenate the query
        self._match += ' %s' % extended_query

        return self.clone()

    def order_by(self, *args):
        """
        Only accepts Neg, C, Columns
        """
        clone = self.clone()

        if not args:
            clone.query.order_by.clear()
            return clone

        for arg in args:
            # parse string
            if isinstance(arg, str):
                if LOOKUP_SEPARATOR in arg:
                    raise NotImplementedError('Django-SphinxQL does not support '
                                              'lookups in order by.')
                if arg[0] == '-':
                    arg = Neg(C(arg[1:]))
                else:
                    arg = C(arg)

            # parse negation of column
            assert isinstance(arg, (Neg, C, Column))
            ascending = True
            if isinstance(arg, Neg):
                ascending = False
                arg = arg.value[0]
                assert isinstance(arg, (C, Column))
            if isinstance(arg, C):
                column = arg.resolve_columns(clone._index)
            else:
                column = arg

            clone.query.order_by.append(column, ascending=ascending)

        return clone

    def _set_default_fields(self, query):
        fields = self._index.Meta.fields

        query.select.clear()
        for field in fields:
            query.select.append(field)

    @staticmethod
    def _add_condition(where, condition):
        if where is None:
            where = condition
        else:
            where = where |And| condition
        return where

    def clone(self):
        clone = QuerySet(self._index)
        clone._match = self._match
        clone.query = self.query.clone()
        return clone


class SearchQuerySet(query.QuerySet):
    """
    A queryset to translate search results into Django models.
    """
    max_search_count = 1000

    def __init__(self, index, query=None, using=None):
        super(SearchQuerySet, self).__init__(index.Meta.model, query, using)
        self._index = index
        self._sphinx_queryset = QuerySet(index)

        self._result_cache = None
        self.search_mode = False

    def search_filter(self, *conditions, **lookups):
        clone = self._clone()
        clone._sphinx_queryset = self._sphinx_queryset.filter(*conditions, **lookups)
        return clone

    def search(self, *extended_queries):
        clone = self._clone()
        clone.search_mode = True
        clone._sphinx_queryset = clone._sphinx_queryset.search(*extended_queries)
        if not clone._sphinx_queryset.query.order_by:
            clone = clone.search_order_by(C('@relevance'))
        return clone

    def search_order_by(self, *columns):
        clone = self._clone()
        clone._sphinx_queryset = clone._sphinx_queryset.order_by(*columns)
        return clone

    def _annotated_models(self):
        """
        Returns the models annotated with `search_result`. Uses `_result_cache`.
        """
        if self._result_cache is not None:
            return self._result_cache

        # hit Sphinx: ordered results with index objects populated
        indexes = OrderedDict([(index_obj.id, index_obj)
                               for index_obj in self._sphinx_queryset[:self.max_search_count]])

        # hit Django: ordered results with model objects populated
        clone = self._get_query(indexes.keys())
        models = OrderedDict([(obj._get_pk_val(), obj) for obj in clone])

        # exclude objects excluded by Django query
        # annotate models with search_result.
        self._result_cache = []
        if self._sphinx_queryset.query.order_by:
            for id in indexes:
                if id in models:
                    # annotate `search_result`
                    models[id].search_result = indexes[id]
                    self._result_cache.append(models[id])
        else:
            for id in models:
                # annotate `search_result`
                models[id].search_result = indexes[id]
                self._result_cache.append(models[id])
        return self._result_cache

    def _get_query(self, id_list=None):
        """
        Returns a Django queryset restricted to the ids in `id_list`.
        If `id_list` is None, hits Sphinx to retrieve it.
        """
        if id_list is None:
            id_list = [index_obj.id for index_obj in self._sphinx_queryset[:self.max_search_count]]
        clone = self._clone()
        clone = clone.filter(pk__in=id_list)
        clone.search_mode = False
        return clone

    def __iter__(self):
        if self.search_mode:
            return iter(self._annotated_models())
        return super(SearchQuerySet, self).__iter__()

    def __len__(self):
        if self.search_mode:
            return len(self._get_query())
        return super(SearchQuerySet, self).__len__()

    def __getitem__(self, item):
        if self.search_mode:
            return self._annotated_models()[item]
        return super(SearchQuerySet, self).__getitem__(item)

    def count(self):
        if self.search_mode:
            return self._get_query().count()
        return super(SearchQuerySet, self).count()

    def _clone(self, klass=None, setup=False, **kwargs):
        ## almost-copy of original _clone:
        if klass is None:
            klass = self.__class__
        query = self.query.clone()
        if self._sticky_filter:
            query.filter_is_sticky = True
        c = klass(index=self._index, query=query, using=self._db)  # this line is different
        c._for_write = self._for_write
        c._prefetch_related_lookups = self._prefetch_related_lookups[:]
        c._known_related_objects = self._known_related_objects
        c.__dict__.update(kwargs)
        if setup and hasattr(c, '_setup_query'):
            c._setup_query()

        # sphinx related
        c.search_mode = self.search_mode
        c._sphinx_queryset = self._sphinx_queryset.clone()
        return c
