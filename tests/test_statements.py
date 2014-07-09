from unittest import TestCase

from sphinxql.sql import Column
from sphinxql.types import Integer
from sphinxql.core.query import SelectStatement, FromStatement


class SelectStatementTestCase(TestCase):
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


class MockIndex:

    def __init__(self, name):
        self.name = name

    def build_name(self):
        return self.name


class FromStatementTestCase(TestCase):

    def test_basic(self):
        fromm = FromStatement()

        fromm.append(MockIndex('test'))

        self.assertEqual(fromm.sql(), 'test')

    def test_two_indexes(self):
        fromm = FromStatement()

        fromm.append(MockIndex('test'))
        fromm.append(MockIndex('test1'))

        self.assertEqual(fromm.sql(), 'test, test1')

    def test_raise_at_same_names(self):
        fromm = FromStatement()

        fromm.append(MockIndex('test'))
        with self.assertRaises(AssertionError):
            fromm.append(MockIndex('test'))
