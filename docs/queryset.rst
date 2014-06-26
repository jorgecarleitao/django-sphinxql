QuerySet
========

.. currentmodule:: sphinxql.query

This document declares the API of the query set, the object returned
by ``DocumentIndex.objects.all()``.

.. class:: QuerySet

    ``QuerySet`` is a helper for translating the developer ideas into a valid
    SphinxQL expression.

    The QuerySet uses the same ideas as a Django QuerySet: it is lazy, allows
    chaining, and caches results.

    Formally, a ``QuerySet`` is initialized with one parameter, the index it is
    bound to::

        >>> q = QuerySet(DocumentIndex)

    Currently, it can be used to *filter*, *order by* and *search* Django models
    instances:

    .. method:: filter(*conditions)

        Adds where clauses (using ``AND``) to its current query. For instance::

            >>> q = q.filter(a)
            >>> q = q.filter(b)

        is equivalent to::

            >>> q = q.filter(a).filter(b)

        and to::

            >>> q = q.filter(a, b)

        The conditions can be any :doc:`expression` that evaluates to a boolean
        value.

    .. method:: match(extended_query)

        Adds a filter to text-search using Sphinx extended query syntax
        defined by the string ``extended_query``.

        Subsequent calls of this method concatenate the string.

        If no ordering is set on the query, this method sets it to be according to
        relevance of the results given by the text search, formally equivalent to::

            q.match(...).order_by(C('@relevance'))

    .. method:: order_by(*expressions)

        Adds ``ORDER BY`` clauses to the existing ones. For instance::

            >>> q = q.order(a)
            >>> q = q.order(b)

        order results by ``a``, then by ``b``, like Django.
        Use ``order_by()`` to clear the ordering.

        Each expression can only be either ``-C(...)`` or ``C(...)``.

        There are two built-in columns, ``C('@id')`` and ``C('@relevance')``
        that are used to order by Django ``id`` and by relevance of the results,
        respectively.

    You can extract results from a query either iterating over it or slicing it.
    Slicing does not allow further filtering.

    The results are always a list of Django models for convenience.

