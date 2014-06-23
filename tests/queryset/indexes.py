from sphinxql import indexes, fields

from .models import Document


class DocumentIndex(indexes.Index):
    summary = fields.String(model_attr='summary')
    text = fields.Text(model_attr='text')

    date = fields.Date(model_attr='date')
    added_time = fields.DateTime(model_attr='added_time')

    number = fields.Integer(model_attr='number')

    class Meta:
        model = Document
        query = Document.objects.all()
