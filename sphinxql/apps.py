import logging

from django.apps import AppConfig, apps

from sphinxql.configuration import indexes_configurator
from django.db.utils import InternalError, OperationalError

logger = logging.getLogger(__name__)


class SphinxQL(AppConfig):
    name = 'sphinxql'

    def ready(self):
        """
        Loads all indexes and configures Sphinx. When db isn't ready, it logs
        it and doesn't index the models.
        """
        for app in apps.get_app_configs():
            module_name = app.module.__package__ + '.indexes'
            try:
                __import__(module_name)
            except ImportError as e:
                if module_name not in str(e):
                    raise
                # ignore apps without indexes.
                pass

        try:
            indexes_configurator.configure()
            indexes_configurator.output()
        except (InternalError, OperationalError):
            logger.warning('Sphinx was not configured: no database found.')
            pass
