import shutil

from django.conf import settings
from django.test import TestCase

from sphinxql import configuration
from sphinxql.configuration import call_process

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass


class SphinxQLTestCase(TestCase):

    def setUp(self):
        super(SphinxQLTestCase, self).setUp()

        configuration.indexes_configurator.path = settings.INDEXES['PATH'] + '_test'
        # Django does not support apps using its connections on loading, see
        # https://docs.djangoproject.com/en/1.7/ref/applications/#django.apps.AppConfig.ready
        # Doing so picks the wrong database for tests.
        # We reconfigure after loading to get the right test database.
        configuration.indexes_configurator.reconfigure()

        call_process(['mkdir', configuration.indexes_configurator.path], fail_silently=True)

        self.addCleanup(self.cleanup)

    def cleanup(self):
        # This is required between tests because searchd
        # returns results even after removing the indexes.
        configuration.stop()

        shutil.rmtree(configuration.indexes_configurator.path)
        configuration.indexes_configurator.path = settings.INDEXES['PATH']

    def index(self):
        """
        Called on SetUp to index the models for the first time.
        """
        configuration.index()
        configuration.start()

    def reindex(self):
        """
        Called on tests to reindex data if new models are created.
        """
        configuration.index()
