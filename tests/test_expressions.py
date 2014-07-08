from unittest import TestCase, expectedFailure
import datetime

from sphinxql.core.base import Function, Or
from sphinxql.sql import Column, And, In, NotIn, Between, NotBetween
from sphinxql.types import Integer, Bool, Date


class ExpressionTestCase(TestCase):

    def setUp(self):
        self.column = Column(Integer, 'test')
        self.column1 = Column(Integer, 'test1')

    def test_basic(self):
        self.assertEqual(self.column.type(), Integer)
        self.assertEqual(self.column.sql(), '`test`')

        self.column **= 2
        self.assertEqual(self.column.type(), Integer)
        self.assertEqual(self.column.sql(), 'POW(`test`, 2)')

    def test_plus(self):
        r = self.column + self.column1
        self.assertEqual(r.sql(), '`test` + `test1`')

        r = self.column + 2
        self.assertEqual(r.sql(), '`test` + 2')

        r = 2 + self.column
        self.assertEqual(r.sql(), '2 + `test`')

    def test_minus(self):
        r = self.column - 2
        self.assertEqual(r.sql(), '`test` - 2')

        r = -2 + self.column
        self.assertEqual(r.sql(), '-2 + `test`')

        r = -self.column + 2
        self.assertEqual(r.sql(), '-`test` + 2')

        r = 2 - self.column
        self.assertEqual(r.sql(), '2 - `test`')

    def test_times(self):
        r = self.column * 2
        self.assertEqual(r.sql(), '`test` * 2')

        r = 2 * self.column
        self.assertEqual(r.sql(), '2 * `test`')

    def test_divide(self):
        r = self.column / 2
        self.assertEqual(r.sql(), '`test` / 2')

        r = 2 / self.column
        self.assertEqual(r.sql(), '2 / `test`')

    def test_power(self):
        r = self.column ** 2
        self.assertEqual(r.sql(), 'POW(`test`, 2)')

        r = 2 ** self.column
        self.assertEqual(r.sql(), 'POW(2, `test`)')


class BooleansTestCase(TestCase):
    def setUp(self):
        self.column = Column(Integer, 'test')

    def test_equal(self):
        r = self.column == 2
        self.assertEqual(r.type(), Bool)
        self.assertEqual(r.sql(), '`test` = 2')

    def test_neq(self):
        r = self.column != 2
        self.assertEqual(r.type(), Bool)
        self.assertEqual(r.sql(), '`test` != 2')

    def test_neg(self):
        r = ~(self.column != 2)
        self.assertEqual(r.type(), Bool)
        self.assertEqual(r.sql(), 'NOT (`test` != 2)')

    def test_gt(self):
        r = self.column > 2
        self.assertEqual(r.type(), Bool)
        self.assertEqual(r.sql(), '`test` > 2')

    def test_ge(self):
        r = self.column >= 2
        self.assertEqual(r.type(), Bool)
        self.assertEqual(r.sql(), '`test` >= 2')

    def test_lt(self):
        r = self.column < 2
        self.assertEqual(r.type(), Bool)
        self.assertEqual(r.sql(), '`test` < 2')

    def test_le(self):
        r = self.column <= 2
        self.assertEqual(r.type(), Bool)
        self.assertEqual(r.sql(), '`test` <= 2')

    @expectedFailure
    def test_or(self):
        """
        OR not defined in SphinxQL yet.
        """
        r = (self.column <= 2) |Or| (self.column >= 2)
        self.assertEqual(r.type(), Bool)
        self.assertEqual(r.sql(), '(`test` <= 2) OR (`test` >= 2)')

    def test_and(self):
        r = (self.column <= 2) |And| (self.column >= 2)
        self.assertEqual(r.type(), Bool)
        self.assertEqual(r.sql(), '(`test` <= 2) AND (`test` >= 2)')

    def test_two_and(self):
        r = (self.column <= 2) |And| (self.column >= 2) |And| (self.column == 2)
        self.assertEqual(r.type(), Bool)
        self.assertEqual(r.sql(), '((`test` <= 2) AND (`test` >= 2)) AND (`test` = 2)')

    def test_in(self):
        r = self.column |In| (2, 3, 4, 5)
        self.assertEqual(r.type(), Bool)
        self.assertEqual(r.sql(), '`test` IN (2, 3, 4, 5)')

    def test_not_in(self):
        r = self.column |NotIn| (2, 3, 4, 5)
        self.assertEqual(r.type(), Bool)
        self.assertEqual(r.sql(), '`test` NOT IN (2, 3, 4, 5)')

    def test_between(self):
        r = self.column |Between| (2, 3)
        self.assertEqual(r.type(), Bool)
        self.assertEqual(r.sql(), '`test` BETWEEN 2 AND 3')

    def test_not_between(self):
        r = self.column |NotBetween| (2, 3)
        self.assertEqual(r.type(), Bool)
        self.assertEqual(r.sql(), '`test` NOT BETWEEN 2 AND 3')


class OtherTestCase(TestCase):
    def setUp(self):
        self.column = Column(Integer, 'test')

    def test_float(self):

        r = self.column + 2.2

        self.assertEqual(r.type(), Integer)
        self.assertEqual(r.as_sql(), '`test` + 2.200000')

    def test_bool(self):

        r = self.column + True

        self.assertEqual(Bool(True).type(), Bool)
        self.assertEqual(r.type(), Integer)
        self.assertEqual(r.as_sql(), '`test` + TRUE')

    def test_dates(self):

        r = Date(datetime.date(2014, 2, 2)) > datetime.date(2014, 3, 2)

        self.assertEqual(r.type(), Bool)
        self.assertEqual(r.as_sql(), '1391299200 > 1393718400')

    def test_datetimes(self):

        r = Date(datetime.datetime(2014, 2, 2, 12, 12, 12)) > datetime.datetime(2014, 2, 2, 12, 12, 13)

        self.assertEqual(r.type(), Bool)
        self.assertEqual(r.as_sql(), '1391343132 > 1391343133')

    def test_wrong_type(self):
        self.assertRaises(TypeError, Date.__lt__, Date(datetime.datetime(2014, 2, 2)), And)

    def test_wrong_function_arguments(self):
        self.assertRaises(IndexError, Function, [1, 2])
