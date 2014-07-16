from collections import OrderedDict
from copy import deepcopy

from ..configuration.connection import Connection, DEFAULT_LIMIT_COUNT
from ..exceptions import NotSupportedError
from .base import CompilableSQL, All
from .columns import IdColumn, Column

# Sphinx sets a max of 5 columns in order by.
MAX_ORDER_BY_ALLOWED = 5


class Query(CompilableSQL):
    """
    A SphinxQL Query.
    """
    def __init__(self, connection=None):
        self._statements = {
            'select': SelectStatement(),
            'from': FromStatement(),
            'where': None,
            'order_by': OrderByStatement(),
            'limit': None   # `None` or (offset, count)
        }
        self.low_mark, self.high_mark = 0, None

        self._connection = connection
        if connection is None:
            self._connection = Connection()

    def __iter__(self):
        """
        If limits are defined, returns an iterator over all results.
        else, iterates over all results using LIMIT in chunks of
        DEFAULT_LIMIT_COUNT.
        """
        return self._connection.iterator(self.as_sql(), self.get_params())

    def __str__(self):
        return self.as_sql() % tuple("\"%s\"" % x for x in self.get_params())

    def __len__(self):
        return len(list(iter(self)))

    @property
    def select(self):
        return self._statements['select']

    @select.setter
    def select(self, value):
        self._statements['select'] = value

    @property
    def fromm(self):
        return self._statements['from']

    @fromm.setter
    def fromm(self, value):
        self._statements['from'] = value

    @property
    def where(self):
        return self._statements['where']

    @where.setter
    def where(self, value):
        self._statements['where'] = value

    @property
    def order_by(self):
        return self._statements['order_by']

    @property
    def limit(self):
        return self._statements['limit']

    @limit.setter
    def limit(self, value):
        if value is not None:
            assert isinstance(value, tuple)
            assert len(value) == 2 and isinstance(value[0], int) and isinstance(value[1], int)
        self._statements['limit'] = value

    def as_sql(self):
        statements = self._statements.copy()
        if not statements['select']:
            statements['select'] = All()

        query = 'SELECT {select} FROM {from}'

        if statements['where']:
            query += ' WHERE {where}'
        if statements['order_by']:
            query += ' ORDER BY {order_by}'
        if statements['limit']:
            query += ' LIMIT %d, %d' % statements['limit']

        cleaned_statements = {key: value.as_sql() for key, value in
                              statements.items() if value and key != 'limit'}

        return query.format(**cleaned_statements)

    def get_params(self):
        params = []
        for clause in ('select', 'from', 'where'):
            if self._statements[clause]:
                params += self._statements[clause].get_params()
        return params

    def clone(self):
        clone = Query()
        # deep because we want new statements
        clone._statements = deepcopy(self._statements)
        return clone


class SelectStatement(CompilableSQL):

    def __init__(self):
        self._expressions = []
        self._alias = []  # list of alias (string) or None if no alias for expression

    def __len__(self):
        """
        For the existence of query
        """
        return len(self._expressions)

    def clear(self):
        self._expressions.clear()
        self._alias.clear()

    def append(self, expression, alias=None):
        assert (alias is None) or alias not in self._alias

        # first column must be ID
        if not self._expressions:
            self._expressions.append(IdColumn())
            self._alias.append(None)
        self._expressions.append(expression)
        self._alias.append(alias)

    def as_sql(self):
        sql = ''
        first = True
        for pos, alias in enumerate(self._alias):
            if first:
                separator = ''
                first = False
            else:
                separator = ', '

            if alias:
                sql += separator + '%s AS %s' % (self._expressions[pos].as_sql(), alias)
            else:
                sql += separator + self._expressions[pos].as_sql()
        return sql

    def get_params(self):
        params = []
        for x in self._expressions:
            params += x.get_params()
        return params


class FromStatement(CompilableSQL):

    def __init__(self):
        self._indexes = OrderedDict()  # index_name: index

    def append(self, index):
        assert index.build_name() not in self._indexes
        self._indexes[index.build_name()] = index

    def as_sql(self):
        assert self._indexes
        sql = ''

        first = True
        for index_name in self._indexes:
            if first:
                separator = ''
                first = False
            else:
                separator = ', '

            sql += separator + '%s' % index_name

        return sql

    def get_params(self):
        return []


class OrderByStatement(CompilableSQL):
    """
    Used to create order by statements
    """
    _DIRECTION = {True: 'ASC', False: 'DESC'}

    def __init__(self):
        self._columns = []  # columns to as_sql()
        self._directions = []  # 'ASC' or 'DESC'
        self._columns_names = []  # columns names already inside

    def __len__(self):
        """
        For the existence of query
        """
        return len(self._columns)

    def as_sql(self):
        assert self._columns
        sql = ''

        first = True
        for pos, column in enumerate(self._columns):
            if first:
                separator = ''
                first = False
            else:
                separator = ', '

            sql += separator + '%s %s' % (column.as_sql(), self._directions[pos])

        return sql

    def append(self, column, ascending=True):
        assert isinstance(column, Column)
        assert isinstance(ascending, bool)
        if len(self._columns) == MAX_ORDER_BY_ALLOWED:
            raise NotSupportedError("Sphinx only supports up to %s expressions "
                                    "in order by" % MAX_ORDER_BY_ALLOWED)

        direction = self._DIRECTION[ascending]

        if column.name in self._columns_names:
            index = self._columns_names.index(column.name)
            self._columns[index] = column
            self._directions[index] = direction
        else:
            self._columns_names.append(column.name)
            self._columns.append(column)
            self._directions.append(direction)

    def clear(self):
        self._columns.clear()
        self._directions.clear()
        self._columns_names.clear()
