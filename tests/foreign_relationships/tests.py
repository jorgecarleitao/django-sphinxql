import datetime
from sphinxql.core.base import Date

from sphinxql.query import Query

from .indexes import DocumentIndex
from .models import Document, Type, MainType

from tests import SphinxQLTestCase


class IndexTestCase(SphinxQLTestCase):

    def setUp(self):
        super(IndexTestCase, self).setUp()

        main_type = MainType.objects.create(name='MainType1')
        self.date = datetime.datetime.now().date()
        type = Type.objects.create(name='Type1', type=main_type, date=self.date)

        Document.objects.create(type=type, text="What a nice text")
        self.index()

    def test_basic(self):
        query = Query()
        query.fromm.append(DocumentIndex)
        result = list(query)

        self.assertEqual('Type1', result[0][2])
        self.assertEqual('MainType1', result[0][3])
        self.assertEqual('MainType1', result[0][4])
        self.assertEqual('MainType1 Type1', result[0][5])
        self.assertEqual(self.date, Date.to_python(result[0][6]))
