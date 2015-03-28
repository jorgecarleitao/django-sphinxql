import shutil
import os

from django.conf import settings
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

        os.mkdir(settings.INDEXES['path'])

    def index(self):
        """
        Called on SetUp to index the models for the first time.
        """
        configuration.index()
        configuration.start()

    def tearDown(self):
        shutil.rmtree(settings.INDEXES['path'])
        settings.INDEXES['path'] = self._old_path
