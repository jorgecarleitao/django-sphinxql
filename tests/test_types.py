import datetime
from unittest import TestCase

from sphinxql.types import Date, DateTime, Float, String


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


class ConversionsTestCase(TestCase):

    def test_datetimes(self):

        time = datetime.datetime(2014, 2, 2, 12, 12, 12)

        db_value = int(DateTime(time).as_sql())
        self.assertEqual(DateTime.to_python(db_value), time)

    def test_dates(self):

        date = datetime.date(2014, 2, 2)

        db_value = int(Date(date).as_sql())
        self.assertEqual(Date.to_python(db_value), date)

    def test_float(self):

        f = 3.2

        db_value = float(Float(f).as_sql())
        self.assertEqual(Float.to_python(db_value), f)

    def test_string(self):

        string = 'dsadsa sdsadas sd as'

        db_value = String(string).as_sql() % String(string).get_params()[0]
        self.assertEqual(Float.to_python(db_value), string)
