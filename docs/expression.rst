SphinxQL Queries
================

.. currentmodule:: sphinxql

This section of the documentation is about the a low-level API,
i.e. how to construct raw queries. For the high level API, see
:doc:`queryset`.

Sphinx uses a dialect of SQL, SphinxQL, to build queries for searching.
Django-SphinxQL exposes this dialect in Python using a low-level API.

Let's say you want to refer to the column ``column_name``.
In SphinxQL, you would use ``SELECT column_name FROM index_name``.
In Django-SphinxQL, you use the expression ``C``::

    >>> from sphinxql.sql import Query, C
    >>> q = Query()
    >>> q.select.append(C('column_name'))
    >>> q.fromm.append(DocumentIndex)
    >>> print(q.as_sql())

``select`` is a list-like object that accepts any expression. For instance::

    >>> custom_select = C('weight')**2 + C('number')
    >>> q.select.append(custom_select)
    >>> q.select.insert(0, custom_select*2)
    >>> q.fromm.append(index)
    >>> q.sql()
    "SELECT POW(weight,2), POW(weight,2)*2 FROM index_name"

The query is lazy and is executed against the database when you iterate over it,
e.g. using::

    >>> list(q)

To filter results (using ``WHERE``), the notation is the same::

    >>> from sphinxql.sql import And
    >>> q.where = C('weight')**2 + C('votes') < 10
    >>> q.where = q.where |And| (C('votes') > 0)

The following operators are defined:

    * ``|And|``
    * ``|In|``
    * ``|NotIn|``
    * ``|Between|``

Notice that you can also construct queries using datetimes and dates.

SQLExpression
~~~~~~~~~~~~~

.. class:: SQLExpression

    ``SQLExpression`` is an abstract way to build arbitrary SQL expressions.
    Almost everything in Django-SphinxQL is based on it: :class:`fields.Field`,
    ``types.Integer``, ``And``, :class:`types.Value`, etc.

    It has most Python operators overridden such that an expression ``C('foo') + 2``
    is converted into ``Plus(C('foo'), Value(2))``, which can then be represented
    in SQL.

Values
------

.. currentmodule:: sphinxql.types

.. class:: Value

    Subclass of :class:`SQLExpression` for constant values. Implemented by the following
    subclasses:

    * ``Bool``
    * ``Integer``
    * ``Float``
    * ``String``
    * ``Date``
    * ``DateTime``

Any ``SQLExpression`` that encounters a Python type converts it to any of these types.
For instance::

    C('votes') < 10

is automatically translated to ``SmallerThan(C('votes'), Integer(10))``.

Operations
----------

.. currentmodule:: Sphinxql.sql

.. class:: BinaryOperation

    Subclass of :class:`SQLExpression` for binary operations. Implemented by the following
    subclasses:

    * ``Plus``
    * ``Subtract``
    * ``Multiply``
    * ``Divide``
    * ``Equal``
    * ``NotEqual``
    * ``And``
    * ``GreaterThan``
    * ``GreaterEqualThan``
    * ``LessThan``
    * ``LessEqualThan``

Other functions
---------------

* ``In``, ``NotIn``
* ``Between``, ``NotBetween``
* ``Not``

Sphinx extended query syntax
============================

.. _dedicated syntax: sphinxsearch.com/docs/current.html#extended-syntax

To filter results based on text, Sphinx defines a SQL reserved keyword ``MATCH()``.
Inside this function, Sphinx allows a `dedicated syntax`_ to filter text against
the Sphinx index. In Django-Sphinxql, such filter is defined as a string inside a
``Match`` is a string::

    >>> q.where = Match('hello & world') & C('votes') > 0

Sphinx only allows one ``MATCH`` per query; it is the developer responsibility to
guarantee that this happens.
