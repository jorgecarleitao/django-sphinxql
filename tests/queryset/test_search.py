import datetime

from sphinxql.query import SearchQuerySet

from .indexes import DocumentIndex
from .models import Document
from sphinxql.sql import C

from tests import SphinxQLTestCase


class SearchQuerySetTestCase(SphinxQLTestCase):

    def setUp(self):
        super(SearchQuerySetTestCase, self).setUp()

        for x in range(1, 101):
            Document.objects.create(
                summary="This is a summary", text="What a nice text. "*x,
                date=datetime.date(2015, 2, 2) + datetime.timedelta(days=x),
                added_time=datetime.datetime(2015, 4, 4, 12, 12, 12) + datetime.timedelta(days=x),
                number=x*2)

        self.index()

        self.query = SearchQuerySet(DocumentIndex)

    def tearDown(self):
        Document.objects.all().delete()
        super(SearchQuerySetTestCase, self).tearDown()

    def test_search(self):
        query = self.query.filter(number__gt=190)
        self.assertEqual(len(query), 5)

        self.assertEqual(len(query.search('nice')), 5)

        self.assertEqual(len(query.search('@text apple')), 0)
        self.assertEqual(query.search('@text apple').count(), 0)

        self.assertEqual(len(query.search('@text text what')), 5)

        # all with high number have this particular sentence
        self.assertEqual(len(query.search('@text "text. What"')), 5)

        # all except one should have this one
        self.assertEqual(len(self.query.search('@text "text. What"')), 99)

    def test_override_order_by(self):
        query = self.query.order_by('-number')
        self.assertEqual(query[0].number, 200)

        query.search_mode = True
        self.assertEqual(query.search_order_by(C('@id'))[0].number, 2)
