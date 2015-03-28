import logging

from django.apps import AppConfig, apps

from sphinxql.configuration import indexes_configurator
from django.db.utils import InternalError

logger = logging.getLogger(__name__)


class SphinxQL(AppConfig):
    name = 'sphinxql'

    def ready(self):
        """
        Loads all indexes and
        """
        for app in apps.get_app_configs():
            __import__(app.module.__package__ + '.indexes')

        try:
            indexes_configurator.configure()
            indexes_configurator.output()
        except InternalError:
            logger.warning('Sphinx was not configurated: no database found.')
            pass
