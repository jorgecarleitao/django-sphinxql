from django.db.models import F, CharField, Value
from django.db.models.functions import Concat
from sphinxql import indexes, fields

from .models import Document


class DocumentIndex(indexes.Index):
    text = fields.IndexedString(model_attr='text')
    type_name = fields.IndexedString(model_attr='type__name')
    main_type_name = fields.IndexedString(model_attr='type__type__name')
    main_type_name1 = fields.IndexedString(model_attr=F('type__type__name'))
    type_name2 = fields.IndexedString(model_attr=Concat('type__type__name',
                                                        Value(" "), 'type__name',
                                                        output_field=CharField()))
    date = fields.Date(model_attr='type__date')

    class Meta:
        model = Document


class DocumentIndex1(indexes.Index):
    type_name2 = fields.IndexedString(model_attr=Concat('text', Value(" "),
                                                        'text',
                                                        output_field=CharField()))

    class Meta:
        model = Document


class DocumentIndex2(indexes.Index):
    name = fields.IndexedString(Concat(F('type__name'), Value(' '),
                                       output_field=CharField()))
    text = fields.IndexedString('text')

    class Meta:
        model = Document
        range_step = 10000
