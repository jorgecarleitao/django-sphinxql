from unittest import TestCase

from django.utils.timezone import now

from sphinxql.core.base import DateTime, Date
from sphinxql.exceptions import ImproperlyConfigured
from sphinxql.query import Query
from sphinxql.sql import Match
from sphinxql.types import String
from sphinxql import indexes
from sphinxql import fields

from .indexes import DocumentIndex
from .models import Document


from tests import SphinxQLTestCase


class ConfigurationTestCase(TestCase):

    def test_wrong_attribute(self):
        with self.assertRaises(ImproperlyConfigured):
            class Index(indexes.Index):
                wrong_attr = fields.Text(model_attr='summaryERROR')

                class Meta:
                    model = Document


class IndexTestCase(SphinxQLTestCase):

    def setUp(self):
        super(IndexTestCase, self).setUp()

        self.document = Document.objects.create(
            summary="This is a summary", text="What a nice text",
            date=now().date(),
            added_time=now(),
            number=2, float=2.2, bool=True,
            unicode='câmara',
            slash='/summary')
        self.index()

        self.query = Query()
        self.query.fromm.append(DocumentIndex)

    def tearDown(self):
        Document.objects.all().delete()
        super(IndexTestCase, self).tearDown()

    def test_summary(self):
        result = list(self.query)[0][1]
        self.assertEqual(result, 'This is a summary')

    def test_text(self):
        result = list(self.query)[0][2]
        self.assertEqual(result, 'What a nice text')

    def test_date(self):
        result = list(self.query)[0][3]

        result = Date.to_python(result)
        self.assertEqual(result, self.document.date)

    def test_datetime(self):
        result = list(self.query)[0][4]

        result = DateTime.to_python(result)
        self.assertEqual(result, self.document.added_time.replace(microsecond=0))

    def test_number(self):
        result = list(self.query)[0][5]
        self.assertEqual(result, 2)

    def test_float(self):
        result = list(self.query)[0][6]
        self.assertEqual(result, 2.2)

    def test_bool(self):
        result = list(self.query)
        self.assertEqual(len(result), 1)

        result = result[0][7]
        self.assertEqual(result, 1)

    def test_unicode(self):
        self.query.where = Match('@unicode câmara')
        self.assertEqual(len(self.query), 1)

        self.query.where = Match('@unicode c mara')
        self.assertEqual(len(self.query), 0)

    def test_slash(self):
        """
        Issue #6: slashes must be escaped correctly.
        """
        self.query.where = Match('@slash /summary')

        self.assertTrue(r'\/' in str(self.query))
        self.assertEqual(len(self.query), 1)
