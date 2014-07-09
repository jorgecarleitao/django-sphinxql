SphinxQL Queries
================

.. currentmodule:: sphinxql

This section of the documentation explains how to construct these expressions.
To use queries with Django, see :doc:`queryset`.

Sphinx uses a dialect of SQL, SphinxQL, to perform operations on its database.
Django-SphinxQL has a notation equivalent to Django to construct such expressions.

The basic unit of SphinxQL is a column. In Django-SphinxQL, a
:class:`~fields.Field` is a ``Column`` and thus the most explicit way
to identify a column is to use::

    >>> from myapp.indexes import PostIndex
    >>> PostIndex.number  # a column

In a :class:`query.SearchQuerySet`, you can use more implicit but simpler
notations::

    >>> PostIndex.objects.search_filter(number=2)
    >>> from sphinxql.sql import C
    >>> PostIndex.objects.search_filter(C('number') == 2)
    >>> PostIndex.objects.search_filter(PostIndex.number == 2)

The first expression uses Django-equivalent lookups. The second uses
``C('number')``, that is equivalent to Django F-expression and is resolved
by the ``SearchQuerySet`` to ``PostIndex.number`` (or returns an error if
``PostIndex`` doesn't have a :class:`~fields.Field` ``number``).

Given a column, you can apply any Python operator (except bitwise) to it::

    >>> my_expression = C('number')**2 + C('series')
    >>> PostIndex.objects.search_filter(my_expression > 2)
    >>> my_expression += 2
    >>> my_expression = my_expression > 2  # it is now a condition

.. warning::

    Django-SphinxQL still does not type-check operations:
    it can query ``'hi hi' + 2 < 4`` if you write a wrongly-typed expression.

.. _Infix: http://code.activestate.com/recipes/384122-infix-operators/

To use SQL operators not defined in Python, you have two options::

    >>> PostIndex.objects.search_filter(number__in=(2, 3))
    >>> from sphinxql.sql import In
    >>> PostIndex.objects.search_filter(C('number') |In| (2, 3))

Again, the first is the Django way and more implicit; the second is more explicit
and lengthier, but allows you to create complex expressions, and uses Infix_ idiom.

The following operators are defined:

    * ``|And|`` (separate conditions in ``search_filter``)
    * ``|In|`` (``__in``, like Django)
    * ``|NotIn|`` (``__nin``)
    * ``|Between|`` (``__range``, like Django)
    * ``|NotBetween|``  (``__nrange``)

API references
~~~~~~~~~~~~~~

.. warning::

    This part of the documentation is still internal and subject to change/disappear.

SQLExpression
-------------

.. class:: core.base.SQLExpression

    ``SQLExpression`` is the abstraction to build arbitrary SQL expressions.
    Almost everything in Django-SphinxQL is based on it: :class:`fields.Field`,
    ``And``, :class:`types.Value`, etc.

    It has most Python operators overridden such that an expression ``C('foo') + 2``
    is converted into ``Plus(C('foo'), Value(2))``, which can then be represented
    in SQL.

Values
------

.. class:: types.Value

    Subclass of :class:`~core.base.SQLExpression` for constant values.
    Implemented by the following subclasses:

    * ``Bool``
    * ``Integer``
    * ``Float``
    * ``String``
    * ``Date``
    * ``DateTime``

    Any ``SQLExpression`` that encounters a non-SQLExpression type tries to convert
    it to any of these types or raises a ``TypeError``. For instance::

        C('votes') < 10

        is translated to ``SmallerThan(C('votes'), Integer(10))``.


    ``String`` is always SQL-escaped.

Operations
----------

.. class:: sql.BinaryOperation

    Subclass of :class:`~core.base.SQLExpression` for binary operations.
    Implemented by the following subclasses:

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
----------------------------

.. _dedicated syntax: sphinxsearch.com/docs/current.html#extended-syntax

.. class:: sql.Match

    To filter results based on text, Sphinx defines a SQL keyword ``MATCH()``.
    Inside this function, you can use its `dedicated syntax`_ to filter text against
    the Sphinx index. In Django-SphinxQL such filter is defined as a string inside a
    ``Match`` is a string::

        >>> expression = Match('hello & world')

Since Sphinx only allows one ``MATCH`` per query, the public interface for using it
is :meth:`query.SearchQuerySet.search`, that automatically guarantees this.
