from sphinxql import indexes, fields

from .models import Document


class DocumentIndex(indexes.Index):
    my_summary = fields.Text(model_attr='summary')
    my_text = fields.Text(model_attr='text')

    my_date = fields.Date(model_attr='date')
    my_added_time = fields.DateTime(model_attr='added_time')

    my_number = fields.Integer(model_attr='number')

    my_float = fields.Float(model_attr='float')

    my_bool = fields.Bool(model_attr='bool')

    class Meta:
        model = Document
