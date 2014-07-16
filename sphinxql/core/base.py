import datetime
import calendar

from django.conf import settings
from django.utils.timezone import get_current_timezone


def convert(other):
    if isinstance(other, bool):
        return Bool(other)
    if isinstance(other, str):
        return String(other)
    if isinstance(other, int):
        return Integer(other)
    if isinstance(other, float):
        return Float(other)
    if isinstance(other, datetime.datetime):
        return DateTime(other)
    if isinstance(other, datetime.date):
        return Date(other)
    if isinstance(other, SQLExpression):
        return other

    raise TypeError('Cannot convert type "%s"' % type(other))


class CompilableSQL(object):
    """
    An abstract method that defines the API
    to transform itself into a sql expression.
    """
    def as_sql(self):
        """
        Returns the query as an sql without parameters
        """
        raise NotImplementedError

    def get_params(self):
        """
        Returns the list parameters of the query
        """
        raise NotImplementedError('%s' % self.__class__)

    def sql(self):
        """
        Returns the sql expression with substituting parameters
        """
        return self.as_sql() % self.get_params()

    def resolve_columns(self, index):
        return self


class SQLExpression(CompilableSQL):
    """
    A general sql expression.
    """
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        return self._value

    def type(self):
        """
        The output type of the expression (e.g. `Bool`).
        It must return a subclass of `Value`.
        """
        raise NotImplementedError

    def __add__(self, other):
        other = convert(other)
        return Add(self, other)

    def __radd__(self, other):
        other = convert(other)
        return Add(other, self)

    def __sub__(self, other):
        other = convert(other)
        return Subtract(self, other)

    def __rsub__(self, other):
        other = convert(other)
        return Subtract(other, self)

    def __mul__(self, other):
        other = convert(other)
        return Multiply(self, other)

    def __rmul__(self, other):
        other = convert(other)
        return Multiply(other, self)

    def __truediv__(self, other):
        other = convert(other)
        return Divide(self, other)

    def __rtruediv__(self, other):
        other = convert(other)
        return Divide(other, self)

    def __pow__(self, other):
        other = convert(other)
        return Power(self, other)

    def __rpow__(self, other):
        other = convert(other)
        return Power(other, self)

    def __neg__(self):
        return Neg(self)

    ### operators that return bool

    def __eq__(self, other):
        other = convert(other)
        return Equal(self, other)

    def __ne__(self, other):
        other = convert(other)
        return NotEqual(self, other)

    def __ge__(self, other):
        other = convert(other)
        return GreaterEqualThan(self, other)

    def __gt__(self, other):
        other = convert(other)
        return GreaterThan(self, other)

    def __le__(self, other):
        other = convert(other)
        return LessEqualThan(self, other)

    def __lt__(self, other):
        other = convert(other)
        return LessThan(self, other)

    ### operators over bool

    def __invert__(self):
        return Not(self)


class All(CompilableSQL):

    def as_sql(self):
        return '*'

    def get_params(self):
        return []


#### Functions

class Function(SQLExpression):
    """
    Represents any mathematical function x, y, ... -> f(x, y, ...)
    It has arguments and returns a value.
    """
    _function = ''

    # number of arguments; if None use arbitrary (len(self._value))
    _arguments_num = 1

    def __init__(self, values):
        if self._arguments_num is not None and\
           len(values) != self._arguments_num:
            raise IndexError('len of argument of "%s" must be %d' %
                             (self.__class__.__name__, self._arguments_num))
        super(Function, self).__init__(values)

    def type(self):
        """
        By default, the type is of the the first
        argument.
        """
        return self._value[0].type()

    @staticmethod
    def _format_parameters(iterable):
        return ', '.join([value.as_sql() for value in iterable])

    def as_sql(self):
        return '{function}({parameters_sql})'\
            .format(function=self._function,
                    parameters_sql=self._format_parameters(self._value))

    def get_params(self):
        params = []
        for value in self._value:
            params += value.get_params()
        return params

    def resolve_columns(self, index):
        self._value = [value.resolve_columns(index) for value in self._value]
        return super(Function, self).resolve_columns(index)


class UnitaryFunction(Function):
    """
    A helper for 1 argument functions.
    """
    _arguments_num = 1

    def __init__(self, argument):
        super(UnitaryFunction, self).__init__([argument])


class Not(UnitaryFunction):
    def as_sql(self):
        return 'NOT (%s)' % self._value[0].as_sql()


class Neg(UnitaryFunction):
    def as_sql(self):
        return '-%s' % self._value[0].as_sql()


class Match(UnitaryFunction):
    _function = 'MATCH'

    def __init__(self, argument):
        #Match always receives a string
        assert isinstance(argument, str)

        # See issue #6:
        # slash `/` must be escaped on MATCH.
        argument = argument.replace('/', r'\/')

        super(UnitaryFunction, self).__init__([String(argument)])


class Count(UnitaryFunction):
    _function = 'COUNT'


class Power(Function):
    _function = 'POW'
    _arguments_num = 2

    def __init__(self, base, exponent):
        super(Power, self).__init__([base, exponent])


class In(Function):
    _function = 'IN'
    _arguments_num = None

    def type(self):
        return Bool

    def __init__(self, lhs, rhs):
        assert isinstance(rhs, (tuple, set, list))
        values = (lhs,) + tuple(convert(value) for value in rhs)
        super(In, self).__init__(values)

    def as_sql(self):
        return '{lhs} {function} ({rhs})'.format(
            function=self._function,
            lhs=self._value[0].as_sql(),
            rhs=self._format_parameters(self._value[1:]))


class NotIn(In):
    _function = 'NOT IN'


class Between(Function):
    _function = 'BETWEEN'
    _arguments_num = 3

    def type(self):
        return Bool

    def __init__(self, lhs, rhs):
        assert isinstance(rhs, (tuple, set, list))
        assert len(rhs) == 2
        values = (lhs,) + tuple(convert(value) for value in rhs)
        super(Between, self).__init__(values)

    def as_sql(self):
        return '{lhs} {function} {first} AND {second}'.format(
            function=self._function,
            lhs=self._value[0].as_sql(),
            first=self._value[1].as_sql(),
            second=self._value[2].as_sql())


class NotBetween(Between):
    _function = 'NOT BETWEEN'


#### Binary Functions

class BinaryFunction(Function):
    """
    Any function of two arguments that is represented by `<lhs> <operation> <rhs>`
    (e.g. 2 + 3).
    """
    _arguments_num = 2

    def __init__(self, lhs, rhs):
        super(BinaryFunction, self).__init__([lhs, rhs])

    def as_sql(self):
        return '{lhs} {function} {rhs}'.format(function=self._function,
                                               lhs=self._value[0].as_sql(),
                                               rhs=self._value[1].as_sql())


class Add(BinaryFunction):
    _function = '+'


class Subtract(BinaryFunction):
    _function = '-'


class Multiply(BinaryFunction):
    _function = '*'


class Divide(BinaryFunction):
    _function = '/'


#### Boolean Functions

class BooleanOperation(BinaryFunction):
    """
    Represents a binary operation over booleans
    """
    def type(self):
        return Bool


class Equal(BooleanOperation):
    _function = '='


class NotEqual(BooleanOperation):
    _function = '!='


class And(BooleanOperation):
    _function = 'AND'

    def as_sql(self):
        return '({lhs}) {function} ({rhs})'.format(function=self._function,
                                                   lhs=self._value[0].as_sql(),
                                                   rhs=self._value[1].as_sql())


class Or(BooleanOperation):
    _function = 'OR'

    def as_sql(self):
        return '({lhs}) {function} ({rhs})'.format(function=self._function,
                                                   lhs=self._value[0].as_sql(),
                                                   rhs=self._value[1].as_sql())


class GreaterThan(BooleanOperation):
    _function = '>'


class LessThan(BooleanOperation):
    _function = '<'


class LessEqualThan(BooleanOperation):
    _function = '<='


class GreaterEqualThan(BooleanOperation):
    _function = '>='


#### Values

class Value(SQLExpression):
    """
    Represents a constant value.
    """
    _input_python_types = ()
    _python_type = None

    def __init__(self, value):
        if not isinstance(value, self._input_python_types):
            raise TypeError("%s only accepts types %s" %
                            (self.__class__, self._input_python_types))
        if not isinstance(value, self._python_type):
            value = self._python_type(value)
        super(Value, self).__init__(value)

    def type(self):
        return type(self)

    def get_params(self):
        return []

    @staticmethod
    def to_python(db_value):
        return db_value


class Integer(Value):
    _input_python_types = (int, float, bool)
    _python_type = int

    def as_sql(self):
        return '%d' % self._value


class Float(Value):
    _input_python_types = (int, float, bool)
    _python_type = float

    def as_sql(self):
        return '%f' % self._value


class Bool(Value):
    _input_python_types = (int, float, bool)
    _python_type = bool

    def as_sql(self):
        if self._value:
            return 'TRUE'
        else:
            return 'FALSE'


class String(Value):
    _input_python_types = (int, float, bool, str)
    _python_type = str

    def as_sql(self):
        return '%s'

    def get_params(self):
        return [self._value]


class Date(Value):
    _input_python_types = (datetime.date,)
    _python_type = datetime.date

    def as_sql(self):
        return calendar.timegm(self._value.timetuple())

    @staticmethod
    def to_python(db_value):
        dt = datetime.datetime.utcfromtimestamp(db_value)
        if settings.USE_TZ:
            dt = dt.replace(tzinfo=get_current_timezone())
        return dt.date()


class DateTime(Date):
    _input_python_types = (datetime.date, datetime.datetime)
    _python_type = datetime.datetime

    @staticmethod
    def to_python(db_value):
        dt = datetime.datetime.utcfromtimestamp(db_value)
        if settings.USE_TZ:
            dt = dt.replace(tzinfo=get_current_timezone())
        return dt
