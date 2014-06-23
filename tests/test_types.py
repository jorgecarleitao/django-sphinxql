import datetime
from unittest import TestCase

from sphinxql.types import Date, DateTime, Float


class DateTestCase(TestCase):

    def test_date(self):
        self.assertRaises(TypeError, Date, 2)
        self.assertRaises(TypeError, Date, 'sql injection')

        try:
            Date(datetime.date(2013, 2, 2))
        except TypeError:
            self.fail("Date() raised TypeError on date.")

        try:
            Date(datetime.datetime.utcnow())
        except TypeError:
            self.fail("Date() raised TypeError on datetime.")

    def test_datetime(self):
        self.assertRaises(TypeError, DateTime, 2)
        self.assertRaises(TypeError, DateTime, 'sql injection')
        self.assertRaises(TypeError, DateTime, datetime.date(2013, 2, 2))

        try:
            DateTime(datetime.datetime.utcnow())
        except TypeError:
            self.fail("DateTime() raised TypeError on datetime.")

    def test_float(self):
        self.assertRaises(TypeError, Float, 'sql injection')

        try:
            Float(True)
        except TypeError:
            self.fail("Float() raised TypeError on bool.")
