from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from sphinxql import configuration


class Command(BaseCommand):
    help = "Indexes your models."

    def add_arguments(self, parser):
        parser.add_argument(
            '--update',
            action='store_true',
            help='',
            default=True)

    def handle(self, **options):
        self.stdout.write('Started indexing')
        self.stdout.write('----------------')

        if options['update']:
            self.stdout.write(configuration.reindex())
        else:
            self.stdout.write(configuration.index())

        self.stdout.write('-----------------')
        self.stdout.write('Indexing finished')
