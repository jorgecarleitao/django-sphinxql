SphinxQL Queries
================

.. currentmodule:: sphinxql

This section of the documentation explains how to construct expressions.
To use queries with Django, see :doc:`queryset`.

The basic unit of SphinxQL is the :class:`~columns.Column`. In Django-SphinxQL,
a :class:`Field` is a ``Column`` and thus the easiest way to identify a column is
to use::

    >>> from myapp.indexes import PostIndex
    >>> PostIndex.number  # a column

However, in a :class:`SearchQuerySet`, you can use a friendlier notation::


    >>> PostIndex.objects.search_filter(number=2)
    >>> from sphinxql.sql import C
    >>> PostIndex.objects.search_filter(C('number') == 2)
    >>> PostIndex.objects.search_filter(PostIndex.number == 2)

The first expression uses Django-equivalent lookups. The second uses
``C('number')``, that is equivalent to Django F-expression and is resolved
by the ``SearchQuerySet`` to ``PostIndex.number`` (or returns an error if
``PostIndex`` doesn't have a :class:`~fields.Field` ``number``).

Given a column, you can apply any Python operator to it::

    >>> my_expression = C('number')**2 + C('series')
    >>> PostIndex.objects.search_filter(my_expression > 2)
    >>> my_expression += 2
    >>> my_expression = my_expression > 2  # it is now a condition

.. warning::
    Django-SphinxQL still does not type-check operations:
    it can query ``'hi hi' + 2 < 4`` if you pass a wrong type expression.

.. _Infix: http://code.activestate.com/recipes/384122-infix-operators/

To use SQL operators not defined in Python, you have two options::

    >>> PostIndex.objects.search_filter(number__in=(2, 3))
    >>> from sphinxql.sql import In
    >>> PostIndex.objects.search_filter(C('number') |In| (2, 3))

The first expression is Django's way; the second allows you to create complex
expressions and uses Infix_.

The following operators are defined:

    * ``|And|`` (separate conditions in ``search_filter``)
    * ``|In|`` (``__in``, like Django)
    * ``|NotIn|`` (``__nin``)
    * ``|Between|`` (``__range``, like Django)
    * ``|NotBetween|``  (``__nrange``)

API references
--------------

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
~~~~~~

.. currentmodule:: sphinxql.types

.. class:: Value

    Subclass of :class:`SQLExpression` for constant values. Implemented by the
    following subclasses:

    * ``Bool``
    * ``Integer``
    * ``Float``
    * ``String``
    * ``Date``
    * ``DateTime``

Any ``SQLExpression`` that encounters a Python type converts it to any of these
types. For instance::

    C('votes') < 10

is translated to ``SmallerThan(C('votes'), Integer(10))``.

Notice that time intervals are not defined in SphinxQL, so you can only compare
dates and times.

Operations
----------

.. currentmodule:: Sphinxql.sql

.. class:: BinaryOperation

    Subclass of :class:`SQLExpression` for binary operations. Implemented by the
    following subclasses:

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

    >>> expression = Match('hello & world') |AND| (C('votes') > 0)

Sphinx only allows one ``MATCH`` per query; it is the developer responsibility to
guarantee that this happens. :meth:`query.QuerySet.search` automatically guarantees
this.
