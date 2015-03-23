from django.db.models import F, CharField
from django.db.models.functions import Concat, Value
from sphinxql import indexes, fields

from .models import Document


class DocumentIndex(indexes.Index):
    text = fields.Text(model_attr='text')
    type_name = fields.Text(model_attr='type__name')
    main_type_name = fields.Text(model_attr='type__type__name')
    main_type_name1 = fields.Text(model_attr=F('type__type__name'))
    type_name2 = fields.Text(model_attr=Concat('type__type__name', Value("' '"),
                                               'type__name',
                                               output_field=CharField()))
    date = fields.Date(model_attr='type__date')

    class Meta:
        model = Document
