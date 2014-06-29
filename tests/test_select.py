from unittest import TestCase

from sphinxql.sql import Column
from sphinxql.types import Integer
from sphinxql.core.query import SelectStatement


class SelectTestCase(TestCase):
    def test_basic(self):
        select = SelectStatement()

        column = Column(Integer, 'test')

        select.append(column, column.name)

        self.assertEqual(select.as_sql(), '`id`, `test` AS test')

    def test_two_columns(self):
        select = SelectStatement()

        column = Column(Integer, 'test')

        select.append(column, column.name)
        select.append(column*2, 'ss')
        select.append(column*3)

        self.assertEqual(select.sql(), '`id`, `test` AS test, `test` * 2 AS ss, `test` * 3')
