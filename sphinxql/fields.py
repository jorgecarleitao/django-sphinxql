from .core import columns
from . import types


class Field(columns.Column):
    """
    A generic field for indexes.

    attr_name is the attribute it uses from the ORM object.
    """
    _type = None
    _sphinx_field_name = None

    def __init__(self, model_attr):
        super(Field, self).__init__(self._type, None)
        self.model_attr = model_attr

    @property
    def is_attribute(self):
        """
        Returns weather the field is a Sphinx attribute. A Sphinx query only
        returns attributes.
        """
        return self._sphinx_field_name is not None


class Text(Field):
    """
    A Sphinx field (indexed but not stored)
    """
    _sphinx_field_name = None
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


class IndexedString(Field):
    """
    A Sphinx field and attribute (i.e. indexed and stored)
    """
    _sphinx_field_name = 'sql_field_string'
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
