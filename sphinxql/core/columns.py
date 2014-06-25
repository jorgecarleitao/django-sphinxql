from ..core.base import SQLExpression, Integer


def quote(string):
    return "`%s`" % string


class Column(SQLExpression):
    """
    Represents a column in the database.

    _value is the alias of the column, _type is the type
    it represents.
    """
    def __init__(self, type, alias):
        super(Column, self).__init__(alias)
        self._type = type

    def as_sql(self):
        return quote('%s' % self._value)

    def type(self):
        return self._type

    @property
    def name(self):
        return self._value

    def get_params(self):
        return []


class IdColumn(Column):
    """
    Column representing the document id
    """
    def __init__(self):
        super(IdColumn, self).__init__(Integer, 'id')


class WeightColumn(Column):
    """
    Column representing the document id
    """
    def __init__(self):
        super(WeightColumn, self).__init__(Integer, 'weight()')

    def as_sql(self):
        return '%s' % self._value
