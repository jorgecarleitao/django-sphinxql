SearchQuerySet
==============

.. currentmodule:: sphinxql.query

This document presents the API of the Django-SphinxQL queryset, the high-level
API for interacting with Sphinx from Django.

.. class:: SearchQuerySet

    ``SearchQuerySet`` extends Django's ``QuerySet`` to allow searching with
    Sphinx; This search is constructed by ``search*`` methods and is lazily
    applied to the Django QuerySet before it hits Django's database.

    Formally, a ``SearchQuerySet`` is initialized with one parameter, the index
    it is bound to::

        >>> q = SearchQuerySet(index, query=None, using=None)

    that initializes Django's queryset from the :attr:`index.Meta.model`.

    The public API of ``SearchQuerySet`` is the same as ``QuerySet``, with
    the following additional methods:

    * :meth:`search`: for text searching
    * :meth:`search_order_by`: for ordering the results of the search
    * :meth:`search_filter`: for filtering the results of the search

    If you don't use any of these methods, ``SearchQuerySet`` is equivalent to
    a Django ``QuerySet``, and thus can be replaced on your code without any
    change.

    When you apply :meth:`search`, ``SearchQuerySet`` assumes you want
    to use Sphinx on it.

    .. attribute:: search_mode

        Defaults to `False`, and defines whether Sphinx should be used by the
        `SearchQuerySet` during the database hit. Automatically set to `True`
        when :meth:`search` is used.

    When ``search_mode`` is ``True``, before interacting with Django database,
    the queryset performs a search in Sphinx database with the query built from
    the above methods:

    * filtering done by :meth:`search` and :meth:`search_filter` are applied
      before Django's query, restricting the valid ``id``s in the Django's query.
    * if any order is done by :meth:`search_order_by` orders the results,
      the Django order is replaced.

    At most, ``SearchQuerySet`` does 1 database hit in Sphinx's database, followed
    by the Django hit.

    .. _extended query syntax: http://sphinxsearch.com/docs/current.html#extended-syntax

    .. method:: search(*extended_queries)

        Adds a filter to text-search using Sphinx `extended query syntax`_,
        defined by the string ``extended_query``. Subsequent calls of this method
        concatenate the different ``extended_query`` with a space (equivalent to
        an ``AND``).

        This method automatically sets a search order according to relevance of the
        results given by the text search.

        For instance::

            >>> q.search('@text Hello world')

        Searches for models with ``Hello world`` on the field ``text`` and orders
        them by most relevance first.

        It supports arbitrary arguments to automatically restrict the search to a
        specific field; the following are equivalent::

            >>> q.search('@text Hello world @summary "my search"')
            >>> q.search('@text Hello world', '@summary "my search"')

        For convenience, here is a list here some operators (full list `here
        <extended query syntax>`_):

        * And: ``' '`` (a space)
        * Or: ``'|'`` (``'hello | world'``)
        * Not: ``'-'`` or ``'!'`` (e.g. ``'hello -world'``)
        * Mandatory first term, optional second term: ``'MAYBE'`` (e.g.
          ``'hello MAYBE world'``)
        * Phrase match: ``'"<...>"'`` (e.g. '"hello world"'``)
        * Before match: ``'<<'`` (e.g. ``'hello << world'``)

        All arguments passed to this function are SQL-escaped.

    .. method:: search_order_by(*expressions)

        Adds ``ORDER BY`` clauses to Sphinx query. For example::

            >>> q = q.search(a).search_order_by(-C('number'))

        will order first by the search relevance (:meth:`search` added it)
        and then by ``number`` in decreasing order. Use ``search_order_by()`` to
        clear the ordering (default order is by ``id``, like Django).

        Currently, the expressions can only be either ``-C(...)`` or ``C(...)``,
        i.e. you cannot order by ``C(number) + C(other_number)``.

        There are two built-in columns, ``C('@id')`` and ``C('@relevance')``,
        that are used to order by Django ``id`` and by relevance of the results,
        respectively.

        At the moment Django performs the database hit, if there is any ordering,
        it replaces the Django order by.

    .. method:: __getitem__(item)

        Like in Django, returns either a single item or a list. There is one
        important subtlety when using searches:

            *Slicing is made on the Search query*

        This implies that if you order by ``relevance`` and slice the first 20
        elements, Django's query will by applied on top of those 20 entries
        (filtered using ``filter(id__in=[...])``).

        Some times this is not desirable because you can end up with less than
        20 entries, even when there are 20 entries that fulfill the requirements
        you have imposed on the Django filter + Sphinx search.

    .. method:: search_filter(*conditions)

        Adds a filter to the search query.

        This method allows you to mitigate the limitation presented on the
        previous method by directly filtering the search query using
        :doc:`Django-SphinxQL expressions <expression>`.

        Using this filter instead of a Django filter implies that a slice of
        20 entries will return 20 entries with that filter.

    if Sphinx was used, model objects will be annotated with an attribute
    ``search_result`` that contains the ``Index`` with the values retrieved
    from Sphinx.
