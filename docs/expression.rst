SphinxQL Queries
================

.. currentmodule:: sphinxql

This section of the documentation explains how to construct expressions.
To build queries, see :doc:`queryset`.

The basic unit of SphinxQL is the :class:`~columns.Column`. In Django-SphinxQL,
a :class:`Field` is a ``Column`` and thus the easiest way to identify a column is
to use::

    >>> from myapp.indexes import PostIndex
    >>> PostIndex.text  # a column

When using a :class:`QuerySet`, the following statements are equivalent::

    >>> from sphinxql.sql import C
    >>> PostIndex.objects.filter(C('text'))
    >>> PostIndex.objects.filter(PostIndex.text)

``C('text')`` is an helper that is resolved by the ``QuerySet`` to ``PostIndex.text``
(or returns an error if ``PostIndex`` doesn't have a :class:`fields.Field` ``text``).

Given a column, you can apply any Python operator to it::

    >>> my_expression = PostIndex.number**2 + PostIndex.series
    >>> PostIndex.objects.filter(my_expression > 2)
    >>> my_expression += 2
    >>> my_expression = my_expression > 2

.. warning::
    Django-SphinxQL still does not type-check operations:
    it can query ``'hi hi' + 2 < 4`` if you pass a wrong type expression.

.. _Infix: http://code.activestate.com/recipes/384122-infix-operators/

Because Python does not allow to create arbitrary operators, we implement
the so called Infix_::

    >>> from sphinxql.sql import In
    >>> my_expression = PostIndex.number |In| (2, 3)
    >>> my_expression = my_expression |And| (PostIndex.number > -5)

The following operators are defined:

    * ``|And|``
    * ``|In|``
    * ``|NotIn|``
    * ``|Between|``

Time intervals are not defined in SphinxQL, so you can only compare dates
and times.

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

is translated to ``SmallerThan(C('votes'), Integer(10))``.

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

    >>> expression = Match('hello & world') |AND| (C('votes') > 0)

Sphinx only allows one ``MATCH`` per query; it is the developer responsibility to
guarantee that this happens. :meth:`query.QuerySet.search` automatically guarantees
this.
