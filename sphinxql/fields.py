from .core import columns
from . import types


class Field(columns.Column):
    """
    A generic field for indexes.

    attr_name is the attribute it uses
    from the ORM object.
    """
    _type = None

    def __init__(self, model_attr):
        super(Field, self).__init__(self._type, None)
        self.model_attr = model_attr


class Text(Field):
    _sphinx_field_name = 'sql_field_string'
    _type = types.String


class Integer(Field):
    """
    A Sphinx attribute (i.e. not indexed)
    """
    _sphinx_field_name = 'sql_attr_bigint'
    _type = types.Integer


class Float(Field):
    """
    A Sphinx attribute (i.e. not indexed)
    """
    _sphinx_field_name = 'sql_attr_float'
    _type = types.Float


class String(Field):
    """
    A Sphinx attribute (i.e. not indexed)
    """
    _sphinx_field_name = 'sql_attr_string'
    _type = types.String


class DateTime(Field):
    """
    A Sphinx attribute (i.e. not indexed)
    """
    _sphinx_field_name = 'sql_attr_timestamp'
    _type = types.DateTime


class Date(Field):
    _sphinx_field_name = 'sql_attr_timestamp'
    _type = types.Date


class Bool(Field):
    _sphinx_field_name = 'sql_attr_bool'
    _type = types.Bool
