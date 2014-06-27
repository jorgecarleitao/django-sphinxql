from collections import OrderedDict

from .core.query import Query
from .core import base
from sphinxql.exceptions import NotSupportedError
from .types import Bool, String
from .sql import Match, And, Neg, C, Column


class QuerySet(object):

    def __init__(self, index):
        self._index = index
        self.query = Query()
        self.query.fromm.append(index)

        self._queryset = self._index.Meta.model.objects.all()  # Django query

        # Sphinx: there can be only one match per query.
        # This is a global constraint on queries
        # We keep it here.
        self._match = ''

        self._result_cache = None
        self._fetch_cache = None

        self._set_default_fields(self.query)

    def reset_cache(self):
        self._result_cache = None

    @property
    def queryset(self):
        return self._queryset

    @queryset.setter
    def queryset(self, queryset):
        self.reset_cache()
        if queryset.model != self._index.Meta.model:
            raise TypeError("You cannot set Django QuerySet of a different model.")
        self._queryset = queryset

    def _fetch_raw(self):
        """
        Fetches by hitting Sphinx
        """
        if self._fetch_cache is not None:
            return self._fetch_cache

        clone = self.query.clone()
        if self._match:
            clone.where = self._add_condition(clone.where, Match(String(self._match)))

        self._fetch_cache = list(clone)
        return self._fetch_cache

    def _parsed_results(self):
        """
        Hits Sphinx and parses the results into indexes instances.
        """
        for result in self._fetch_raw():
            instance = self._index()

            setattr(instance, 'id', result[0])
            i = 1
            for field in self._index.Meta.fields:
                setattr(instance, field.name, field.type().to_python(result[i]))
                i += 1

            yield instance

    def _annotated_models(self):
        """
        Returns the models annotated with `search_result`. Uses `_result_cache`.
        """
        if self._result_cache is not None:
            return self._result_cache

        # hit Sphinx;
        # ordered results with index objects populated
        indexes = OrderedDict([(index_obj.id, index_obj)
                               for index_obj in self._parsed_results()])

        # hit Django
        models = self.queryset.in_bulk(indexes.keys())

        # exclude objects excluded by Django query
        # annotate models with search_result.
        self._result_cache = []
        for id in indexes:
            if id in models:
                # annotate `search_result`
                models[id].search_result = indexes[id]
                self._result_cache.append(models[id])
        return self._result_cache

    def __iter__(self):
        return iter(self._annotated_models())

    def __len__(self):
        return len(list(iter(self)))

    def __getitem__(self, item):
        if not isinstance(item, (slice, int)):
            raise TypeError
        if isinstance(item, slice):
            if item.stop is None:
                raise NotSupportedError('Sphinx does not support unbounded slicing.')

        if self._result_cache is not None:
            return self._result_cache[item]

        if isinstance(item, slice):
            offset = item.start or 0
            count = item.stop - offset

            clone = self.clone()
            clone.query.limit = (offset, count)
            return list(clone)
        else:
            offset = item
            count = 1
            clone = self.clone()
            clone.query.limit = (offset, count)
            return list(clone)[0]

    def all(self):
        return self

    def _resolve_columns(self, expression):
        return expression.resolve_columns(self._index)

    def filter(self, *conditions):
        clone = self.clone()

        for condition in conditions:
            assert isinstance(condition, base.SQLExpression)
            condition = self._resolve_columns(condition)
            assert condition.type() == Bool
            clone.query.where = self._add_condition(clone.query.where, condition)
        return clone

    def search(self, extended_query):
        assert isinstance(extended_query, str)
        # concatenate the query
        self._match += ' %s' % extended_query

        clone = self.clone()
        if not clone.query.order_by:
            clone = clone.order_by(C('@relevance'))

        return clone

    def order_by(self, *args):
        """
        Sets the order, erasing previous ordering.
        Only accepts Neg, C, Columns
        """
        clone = self.clone()

        if not args:
            clone.query.order_by.clear()
            return clone

        for arg in args:
            assert isinstance(arg, (Neg, C, Column))
            ascending = True
            if isinstance(arg, Neg):
                ascending = False
                arg = arg.value[0]
            if isinstance(arg, Column):
                column = arg
            else:
                column = arg.resolve_columns(clone._index)

            clone.query.order_by.append(column, ascending=ascending)

        return clone

    def _set_default_fields(self, query):
        fields = self._index.Meta.fields

        query.select.clear()
        for field in fields:
            query.select.append(field)

    @staticmethod
    def _add_condition(where, condition):
        if where is None:
            where = condition
        else:
            where = where |And| condition
        return where

    def clone(self):
        clone = QuerySet(self._index)
        clone._match = self._match
        clone.query = self.query.clone()
        clone.queryset = self.queryset
        return clone
