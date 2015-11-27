import shutil
import os

from io import StringIO
from django.conf import settings
from django.core.management import call_command
from django.test import TransactionTestCase

from sphinxql import configuration

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass


class SphinxQLTestCase(TransactionTestCase):

    def setUp(self):
        super(SphinxQLTestCase, self).setUp()

        self._old_path = settings.INDEXES['path']
        settings.INDEXES['path'] += '_test'

        # Django does not support apps using its connections on loading, see
        # https://docs.djangoproject.com/en/1.7/ref/applications/#django.apps.AppConfig.ready
        # Doing so picks the wrong database for tests.
        # We reconfigure after loading to get the right test database.
        configuration.indexes_configurator.configure()
        configuration.indexes_configurator.output()

        # clean path if it exists from previous tests
        if os.path.exists(settings.INDEXES['path']):
            shutil.rmtree(settings.INDEXES['path'])
        os.mkdir(settings.INDEXES['path'])

        call_command('index_sphinx', update=False, stdout=StringIO())
        call_command('start_sphinx', stdout=StringIO())

    def index(self):
        """
        Used to reindex the sphinx index.
        """
        call_command('index_sphinx', stdout=StringIO())

    def tearDown(self):
        call_command('stop_sphinx', stdout=StringIO())
        shutil.rmtree(settings.INDEXES['path'])
        settings.INDEXES['path'] = self._old_path
        super(SphinxQLTestCase, self).tearDown()
