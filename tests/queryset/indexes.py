from sphinxql.manager import IndexManager
from sphinxql import indexes, fields

from .models import Document


class Manager(IndexManager):

    def get_queryset(self):
        return super(Manager, self).get_queryset().filter(number__in=[2, 4, 6])


class DocumentIndex(indexes.Index):
    summary = fields.String(model_attr='summary')
    text = fields.IndexedString(model_attr='text')

    date = fields.Date(model_attr='date')
    added_time = fields.DateTime(model_attr='added_time')

    number = fields.Integer(model_attr='number')

    other_objects = Manager()
    objects = IndexManager()

    class Meta:
        model = Document
