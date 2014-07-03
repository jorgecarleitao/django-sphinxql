from . import base

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

