import datetime
from unittest import expectedFailure

from sphinxql.core.base import Or
from sphinxql.exceptions import NotSupportedError
from sphinxql.query import QuerySet
from sphinxql.sql import C, Between

from .indexes import DocumentIndex
from .models import Document

from tests import SphinxQLTestCase


class SimpleTestCase(SphinxQLTestCase):

    def setUp(self):
        super(SimpleTestCase, self).setUp()

        self.document = Document.objects.create(
            summary="This is a summary", text="What a nice text",
            date=datetime.date(2015, 2, 2),
            added_time=datetime.datetime(2015, 4, 4, 12, 12, 12),
            number=2)

        # retrieve data as it is stored in DB
        self.document = Document.objects.get(id=self.document.id)

        self.index()

        self.query = QuerySet(DocumentIndex)

    def tearDown(self):
        Document.objects.all().delete()
        super(SphinxQLTestCase, self).tearDown()


class SimpleQuerySetTestCase(SimpleTestCase):
    """
    Tests basic operations of QuerySet
    """
    def test_lookup_fail(self):
        self.assertRaises(KeyError, self.query.filter, C('numberERROR') >= 2)

    def test_filter(self):
        self.assertEqual(len(self.query), 1)

        q = self.query.filter(C('number') >= 2)
        self.assertEqual(len(q), 1)

        q = self.query.filter(C('number') < 2)
        self.assertEqual(len(q), 0)

    def test_filter_between_integer(self):

        self.query = self.query.filter(C('number') |Between| (1, 3))
        self.assertEqual(len(self.query), 1)

        self.query = self.query.filter(C('number') |Between| (10, 20))
        self.assertEqual(len(self.query), 0)

    def test_filter_between_dates(self):
        self.query = self.query.filter(C('date') |Between| (datetime.date(2014, 1, 1),
                                                            datetime.date(2016, 1, 1)))
        self.assertEqual(len(self.query), 1)

        self.query = self.query.filter(C('date') |Between| (datetime.date(2000, 1, 1),
                                                            datetime.date(2001, 1, 1)))
        self.assertEqual(len(self.query), 0)

    def test_filter_between_datetimes(self):
        self.query = self.query.filter(C('added_time') |Between| (datetime.datetime(2014, 1, 1),
                                                                  datetime.datetime(2016, 1, 1)))
        self.assertEqual(len(self.query), 1)

        self.query = self.query.filter(C('added_time') |Between| (datetime.datetime(2000, 1, 1),
                                                                  datetime.datetime(2001, 1, 1)))
        self.assertEqual(len(self.query), 0)

    def test_two_filters(self):
        q = self.query.filter(C('number') >= 2)
        q = q.filter(C('date') == datetime.date(2015, 2, 2))
        self.assertEqual(len(q), 1)

    @expectedFailure
    def test_exclude(self):
        """
        SphinxQL doesn't seem to accept queries of the form
        "WHERE NOT condition".
        """
        q = self.query.filter(~(C('number') == 2))
        self.assertEqual(len(q), 0)

    @expectedFailure
    def test_filter_string(self):
        """
        Sphinx does not allow filter strings using SQL:
        http://sphinxsearch.com/bugs/view.php?id=1652
        """
        q = self.query.filter(C('summary') == 'This')
        self.assertEqual(len(q), 0)

    def test_search(self):
        q = self.query.search('@text NICE')
        self.assertEqual(len(q), 1)

        q = self.query.search('@text DDDDFDFD')
        self.assertEqual(len(q), 0)

    @expectedFailure
    def test_or(self):
        """
        OR not defined in SphinxQL
        """
        q = self.query.filter(Or(C('number') == 2, C('number') > 2))
        self.assertEqual(len(q), 1)

    @expectedFailure
    def test_compare_columns(self):
        """
        SphinxQL does not allow comparison of columns.
        """
        q = self.query.filter(C('added_time') > C('date'))
        self.assertEqual(len(q), 1)

    def test_date_comparison(self):
        q = self.query.filter(C('date') > datetime.datetime.now())
        self.assertEqual(len(q), 1)

    def test_main_sql(self):
        sql = self.query.query.as_sql()
        self.assertEqual(sql, 'SELECT `id`, `summary`, `text`, `date`, `added_time`, `number` '
                              'FROM queryset_documentindex')

    def test_check_fields(self):
        results = list(self.query)
        self.assertEqual(len(results), 1)

        self.assertEqual(results[0].summary, self.document.summary)
        self.assertEqual(results[0].text, self.document.text)
        self.assertEqual(results[0].date, self.document.date)
        self.assertEqual(results[0].added_time, self.document.added_time)
        self.assertEqual(results[0].number, self.document.number)


class QuerySetLookupTestCase(SimpleTestCase):

    def test_only_1_lookup(self):
        with self.assertRaises(NotImplementedError):
            self.query.filter(string__upper__gte=2)

    def test_invalid_lookup(self):
        with self.assertRaises(KeyError):
            self.query.filter(number__gteERROR=2)

    def test_filter(self):
        self.assertEqual(len(self.query), 1)

        q = self.query.filter(number__gte=2)
        self.assertEqual(len(q), 1)

        q = self.query.filter(number__lt=2)
        self.assertEqual(len(q), 0)

    def test_single_column(self):
        q = self.query.filter(number=2)
        self.assertEqual(len(q), 1)

    def test_order_by_lookup(self):
        with self.assertRaises(NotImplementedError):
            self.query.order_by('number__max')

    def test_order_by(self):
        q = self.query.order_by('number')
        self.assertEqual(len(q), 1)

        q = self.query.order_by('-number')
        self.assertEqual(len(q), 1)


class QuerySetTestCase(SphinxQLTestCase):

    def setUp(self):
        super(QuerySetTestCase, self).setUp()

        for x in range(1, 101):
            Document.objects.create(
                summary="This is a summary", text="What a nice text. "*x,
                date=datetime.date(2015, 2, 2) + datetime.timedelta(days=x),
                added_time=datetime.datetime(2015, 4, 4, 12, 12, 12),
                number=x*2)

        self.index()

    def tearDown(self):
        Document.objects.all().delete()
        super(QuerySetTestCase, self).tearDown()

    def test_len(self):
        self.assertEqual(len(QuerySet(DocumentIndex)), 100)
        self.assertEqual(QuerySet(DocumentIndex).count(), 100)

        self.assertEqual(len(QuerySet(DocumentIndex).search('@text adasdsa')), 0)
        self.assertEqual(QuerySet(DocumentIndex).search('@text adasdsa').count(), 0)

    def test_getitem(self):
        query = QuerySet(DocumentIndex)

        self.assertEqual(len(query), 100)
        self.assertEqual(len(query[:20]), 20)

        self.assertEqual(len(query[90:110]), 10)

        self.assertRaises(NotSupportedError, query.__getitem__, slice(90, None))

        self.assertEqual(query[0].number, 2)

    def test_order_by(self):
        q = QuerySet(DocumentIndex).order_by(C('number'))
        self.assertEqual(q[0].number, 2)

        q = QuerySet(DocumentIndex).order_by(-C('number'))
        self.assertEqual(q[0].number, 200)

        q = QuerySet(DocumentIndex).search('@text What').order_by(C('@relevance'))
        # most relevance is last, because has the most occurrences.
        self.assertEqual(q[0].number, 200)

        # other ordering
        q = QuerySet(DocumentIndex).search('@text What').order_by(C('number'))
        self.assertEqual(q[0].number, 2)
