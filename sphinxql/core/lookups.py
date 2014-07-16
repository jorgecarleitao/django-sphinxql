from . import base
from .. import sql

LOOKUPS = {'eq': base.Equal,
           'neq': base.NotEqual,
           'lt': base.LessThan,
           'gt': base.GreaterThan,
           'lte': base.LessEqualThan,
           'gte': base.GreaterEqualThan,
           'in': base.In,
           'nin': base.NotIn,
           'range': base.Between,
           'nrange': base.NotBetween}

LOOKUP_SEPARATOR = '__'


def parse_lookup(lhs, rhs):
    assert lhs
    parts = lhs.split(LOOKUP_SEPARATOR)

    if len(parts) > 2:
        raise NotImplementedError('Currently Django-SphinxQL only accepts'
                                  'lookups having up to 1 \'__\'.')

    if len(parts) == 1:
        parts.append('eq')

    if parts[0] == 'id':
        column = sql.C('@id')
    else:
        column = sql.C(parts[0])
    lookup = parts[1]

    try:
        operation = LOOKUPS[lookup]
    except KeyError:
        raise KeyError('Lookup \'{0}\' not valid. '
                       'Check documentation on available lookups.'
                       .format(parts[1]))

    if lookup not in ('in', 'nin', 'range', 'nrange'):
        rhs = base.convert(rhs)

    return operation(column, rhs)
