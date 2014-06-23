from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from sphinxql import configuration


class Command(BaseCommand):
    help = "Indexes your models."
    option_list = BaseCommand.option_list

    def handle(self, **options):
        self.stdout.write('Started indexing\n')
        self.stdout.write('----------------\n')

        self.stdout.write(configuration.index())

        self.stdout.write('-----------------\n')
        self.stdout.write('Indexing finished\n')
