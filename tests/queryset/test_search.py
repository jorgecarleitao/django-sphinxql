import datetime

from django.db.models import Sum

from sphinxql.query import SearchQuerySet
from sphinxql.sql import C

from .indexes import DocumentIndex
from .models import Document

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

    def test_django_filter(self):
        query = self.query.filter(number__gt=190)
        self.assertEqual(len(query), 5)
        self.assertEqual(query[0].number, 192)

        q = query.search('@text text. What')
        self.assertEqual(len(q), 5)
        self.assertEqual(q[0].number, 200)

        q = query.search('@text text. What').search_order_by(-C('@relevance'))
        self.assertEqual(len(q), 5)
        self.assertEqual(q[0].number, 192)

    def test_search_filter(self):
        self.assertEqual(len(self.query), 100)
        # all except one should have this one
        self.assertEqual(len(self.query.search('@text "text. What"')), 99)

    def test_override_order_by(self):
        # order by in Django means first number is 200
        query = self.query.order_by('-id')
        self.assertEqual(query[0].number, 200)

        # don't override Django order means first number is 200
        query.search_mode = True
        query = query.search_order_by(C('@id'))
        self.assertEqual(query[0].number, 200)

        # clear Django ordering overrides it; order becomes @id.
        query = query.order_by()
        self.assertEqual(query[0].number, 2)

    def test_iter(self):
        q = self.query.search('@text What').search_order_by()
        i = 1
        for x in q:
            self.assertEqual(x.number, i*2)
            i += 1

    def test_change_queryset(self):

        q = self.query.search('@text What')
        q = q.filter(number__lte=40)
        self.assertEqual(len(q), 20)

        q = q.annotate(sum=Sum('number'))
        for x in q:
            self.assertTrue(hasattr(x, 'sum'))

    def test_data_is_cached(self):
        query = self.query.all()
        with self.assertNumQueries(1):
            list(query)
            list(query)

    def test_one_django_hit(self):
        query = self.query.all()
        with self.assertNumQueries(1):
            len(query)
            query[0:20]
            list(query)

    def test_search_override_default_ordering(self):
        self.assertEqual(self.query[0].number, 2)

        q = self.query.search('@text What')
        self.assertEqual(q[0].number, 200)

    def test_search_doesnt_override_ordering(self):
        q = self.query.search_order_by(C('number'))
        self.assertEqual(q[0].number, 2)

        q = q.search('@text What')
        self.assertEqual(q[0].number, 2)

    def test_django_ordering_override(self):
        # this adds a search_order_by
        q = self.query.search('@text What')
        q1 = self.query.order_by('number')
        self.assertEqual(q[0].number, 200)
        self.assertEqual(q1[0].number, 2)

        # Django order is not ignored
        q = q.order_by('number')
        self.assertEqual(q[0].number, 2)

    def test_django_order_not_overridden(self):
        q = self.query.search('@text What').search_order_by()
        self.assertEqual(q[0].number, 2)

        q = q.order_by('-number')
        self.assertEqual(q[0].number, 200)

    def test_manager(self):
        # test that `objects` work.
        q = DocumentIndex.objects.search('@text What')
        self.assertEqual(q[0].number, 200)

        self.assertEqual(DocumentIndex.objects.count(), 100)

        self.assertEqual(DocumentIndex.objects
                         .filter(number__in=[2, 4, 6]).count(), 3)

        self.assertEqual(DocumentIndex.other_objects.count(), 3)


class HighNumberSearchQuerySetTestCase(SphinxQLTestCase):
    """
    Test for the case with more than 1000 entries
    """
    def setUp(self):
        super(HighNumberSearchQuerySetTestCase, self).setUp()

        for x in range(1, 1005):
            Document.objects.create(
                summary="This is a summary", text="What a nice text.",
                date=datetime.date(2015, 2, 2) + datetime.timedelta(days=x),
                added_time=datetime.datetime(2015, 4, 4, 12, 12, 12) + datetime.timedelta(days=x),
                number=x)

        self.index()

        self.query = SearchQuerySet(DocumentIndex)

    def test_len(self):
        self.assertEqual(len(self.query.search('nice')), 1000)
        self.assertEqual(self.query.search('nice').count(), 1000)

    def test_django_len(self):
        query = self.query.filter(number__gte=95)  # exclude id in [1,94]
        self.assertEqual(len(query), 910)
        self.assertEqual(query.count(), 910)

        # since search results are ordered by id, they are ids 1-1000,
        # thus, the first 94 (id 1-94) + last 5 (id 1000-1005) are discarded
        self.assertEqual(len(query.search('@text nice')), 906)
        self.assertEqual(query.search('nice').count(), 906)

        query = query.search_order_by(-C('@id'))
        self.assertEqual(len(query.search('@text nice')), 910)
        self.assertEqual(query.search('nice').count(), 910)
