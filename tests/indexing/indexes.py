from sphinxql import indexes, fields

from .models import Document


class DocumentIndex(indexes.Index):
    my_summary = fields.IndexedString(model_attr='summary')
    my_text = fields.IndexedString(model_attr='text')

    my_date = fields.Date(model_attr='date')
    my_added_time = fields.DateTime(model_attr='added_time')

    my_number = fields.Integer(model_attr='number')

    my_float = fields.Float(model_attr='float')

    my_bool = fields.Bool(model_attr='bool')

    unicode = fields.IndexedString(model_attr='unicode')

    slash = fields.IndexedString(model_attr='slash')

    class Meta:
        model = Document
        range_step = 100
