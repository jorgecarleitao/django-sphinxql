from .core import columns
from . import types


class Field(columns.Column):
    """
    A generic field for indexes.

    attr_name is the attribute it uses
    from the ORM object.
    """

    def __init__(self, type, model_attr):
        super(Field, self).__init__(type, None)
        self.model_attr = model_attr


class Text(Field):
    _sphinx_field_name = 'sql_field_string'

    def __init__(self, model_attr):
        super(Text, self).__init__(types.String, model_attr)


class Integer(Field):
    """
    A Sphinx attribute (i.e. not indexed)
    """
    _sphinx_field_name = 'sql_attr_bigint'

    def __init__(self, model_attr):
        super(Integer, self).__init__(types.Integer, model_attr)


class Float(Field):
    """
    A Sphinx attribute (i.e. not indexed)
    """
    _sphinx_field_name = 'sql_attr_float'

    def __init__(self, model_attr):
        super(Float, self).__init__(types.Float, model_attr)


class String(Field):
    """
    A Sphinx attribute (i.e. not indexed)
    """
    _sphinx_field_name = 'sql_attr_string'

    def __init__(self, model_attr):
        super(String, self).__init__(types.String, model_attr)


class DateTime(Field):
    """
    A Sphinx attribute (i.e. not indexed)
    """
    _sphinx_field_name = 'sql_attr_timestamp'

    def __init__(self, model_attr):
        super(DateTime, self).__init__(types.DateTime, model_attr)


class Date(Field):
    _sphinx_field_name = 'sql_attr_timestamp'

    def __init__(self, model_attr):
        super(Date, self).__init__(types.Date, model_attr)


class Bool(Field):
    _sphinx_field_name = 'sql_attr_bool'

    def __init__(self, model_attr):
        super(Bool, self).__init__(types.Bool, model_attr)
