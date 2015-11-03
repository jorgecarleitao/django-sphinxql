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

        # clean path if it exists from previous tests
        if os.path.exists(settings.INDEXES['path']):
            shutil.rmtree(settings.INDEXES['path'])
        os.mkdir(settings.INDEXES['path'])

        configuration.index()
        configuration.start()

    def index(self):
        """
        Used to reindex the sphinx index.
        """
        configuration.reindex()

    def tearDown(self):
        configuration.stop()
        shutil.rmtree(settings.INDEXES['path'])
        settings.INDEXES['path'] = self._old_path
        super(SphinxQLTestCase, self).tearDown()
