from sphinxql import indexes, fields

from .models import Author


class AuthorIndex(indexes.Index):
    first_name = fields.IndexedString(model_attr='first_name')
    last_name = fields.IndexedString(model_attr='last_name')
    number = fields.Integer(model_attr='number')
    time = fields.DateTime(model_attr='time')

    class Meta:
        model = Author
        query = Author.objects.all()


class Author2Index(indexes.Index):
    first_name = fields.IndexedString(model_attr='first_name')

    class Meta:
        model = Author
        query = Author.objects.all()
