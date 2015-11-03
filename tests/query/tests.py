import datetime

from sphinxql.core.query import Query
from sphinxql.sql import Match
from sphinxql.types import String

from .indexes import AuthorIndex, Author2Index
from .models import Author

from tests import SphinxQLTestCase


class QueryTestCase(SphinxQLTestCase):

    def setUp(self):
        super(QueryTestCase, self).setUp()

        Author.objects.create(first_name='foo', last_name='bar', number=1,
                              time=datetime.datetime(2014, 2, 2, 12, 12, 12))
        self.index()

        self.query = Query()
        self.query.fromm.append(AuthorIndex)

    def test_basic(self):
        column = AuthorIndex.first_name

        self.query.select.append(column, 'name')

        self.assertEqual(self.query.sql(), 'SELECT `id`, `first_name` AS name FROM query_authorindex')

    def test_two_selects(self):
        column = AuthorIndex.number

        self.query.select.append(column, column.name)
        self.query.select.append(column*2, 'ss')

        self.assertEqual(self.query.sql(), 'SELECT `id`, `number` AS number, `number` * 2 AS ss '
                                           'FROM query_authorindex')

    def test_two_froms(self):
        self.query.fromm.append(Author2Index)

        self.assertEqual(self.query.sql(), 'SELECT * '
                                           'FROM query_authorindex, query_author2index')

    def test_with_where(self):
        column = AuthorIndex.number

        self.query.select.append(column, column.name)
        self.query.where = column*2 > 2

        self.assertEqual(self.query.sql(), 'SELECT `id`, `number` AS number FROM query_authorindex '
                                           'WHERE `number` * 2 > 2')

    def test_sql_order_by(self):
        column = AuthorIndex.number

        self.query.order_by.append(column, ascending=True)

        self.assertEqual(self.query.sql(), 'SELECT * FROM query_authorindex '
                                           'ORDER BY `number` ASC')

        self.query.order_by.append(column, ascending=False)

        self.assertEqual(self.query.sql(), 'SELECT * FROM query_authorindex '
                                           'ORDER BY `number` DESC')

        self.query.order_by.append(AuthorIndex.time, ascending=True)

        self.assertEqual(self.query.sql(), 'SELECT * FROM query_authorindex '
                                           'ORDER BY `number` DESC, `time` ASC')

    def test_all(self):
        self.assertEqual(self.query.sql(), 'SELECT * FROM query_authorindex')

    def test_execute(self):
        self.assertEqual(len(self.query), 1)

    def test_results(self):
        results = list(self.query)
        self.assertEqual(len(results), 1)
        results = results[0]

        self.assertEqual(results[1], 'foo')
        self.assertEqual(results[2], 'bar')
        self.assertEqual(results[3], 1)

    def test_limit(self):
        results = list(self.query)
        self.assertEqual(len(results), 1)

        self.query.limit = (0, 10)
        results = list(self.query)
        self.assertEqual(len(results), 1)

        self.query.limit = (2, 10)
        results = list(self.query)
        self.assertEqual(len(results), 0)

    def test_match(self):
        self.query.where = Match("foo")
        self.assertEqual(len(self.query), 1)
