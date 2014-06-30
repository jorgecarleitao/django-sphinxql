from .core.base import Match, Neg, Count, All
from .core.columns import Column, IdColumn, WeightColumn


import sphinxql.core.base


class C(sphinxql.core.base.SQLExpression):
    """
    The only element capable of resolving columns
    from strings.
    """
    def resolve_columns(self, index):
        """
        Returns the ``Field`` (that is, a Column) of an ``Index`` from its name.
        """
        if self._value == '@id':
            return IdColumn()
        elif self._value == '@relevance':
            return WeightColumn()

        try:
            return index.__dict__[self._value]
        except KeyError:
            raise KeyError('Field "%s" not found in "%s"' %
                           (self._value, index.__name__))


class _Infix:
    """
    Define an arbitrary operator.

    Minimalistic code from
    http://code.activestate.com/recipes/384122-infix-operators/
    """
    def __init__(self, function):
        self.function = function

    def __ror__(self, other):
        return _Infix(lambda x, self=self, other=other: self.function(other, x))

    def __or__(self, other):
        return self.function(other)


@_Infix
def And(one, other):
    return sphinxql.core.base.And(one, other)


@_Infix
def In(element, set):
    return sphinxql.core.base.In(element, set)


@_Infix
def NotIn(element, set):
    return sphinxql.core.base.NotIn(element, set)


@_Infix
def Between(element, set):
    return sphinxql.core.base.Between(element, set)

@_Infix
def NotBetween(element, set):
    return sphinxql.core.base.NotBetween(element, set)
