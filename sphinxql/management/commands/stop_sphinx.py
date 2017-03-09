from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from sphinxql import configuration


class Command(BaseCommand):
    help = 'Interacts with search deamon.'

    def handle(self, **options):
        self.stdout.write('Stopping Sphinx')
        self.stdout.write('---------------')

        self.stdout.write(configuration.stop())

        self.stdout.write('----')
        self.stdout.write('Done')
