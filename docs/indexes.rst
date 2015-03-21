Indexes API
===========

.. currentmodule:: sphinxql

This document explains how Django-SphinxQL maps a Django model into a Sphinx
index.

Sphinx uses a SQL query to retrieve data from a relational database to index it.
This means that Django-SphinxQL must know:

1. what you want to index (e.g. what data)
2. how you want to index it (e.g. type)

In the same spirit of Django, Django-SphinxQL defines an ORM for you to answer
those questions. It works like this::

    # indexes.py
    from sphinxql import fields, indexes
    from myapp import models

    class PostIndex(indexes.Index):
        text = fields.Text('text')  # Post has the model field ``text``
        date = fields.Date('added_date')
        summary = fields.Text('summary')

        class Meta:
            model = models.Post  # the model we are indexing

The ``fields`` and the ``Meta.model`` identify "what"; the specific field type,
e.g. ``Text``, identifies the "how". In the following sections the complete API
is presented.

API references
--------------

Index
~~~~~

.. class:: indexes.Index

    :class:`~indexes.Index` is an ORM to Sphinx-index a Django Model. It works in
    a similar fashion to a Django model: you set up the :class:`fields
    <fields.Field>`, and it constructs an Sphinx index out of those fields.

    Formally, when an index is declared, it is automatically registered in the
    :class:`~sphinxql.configuration.configurators.IndexConfigurator` to
    Django-SphinxQL configure Sphinx.

    An index is always composed by two components: a set of :class:`fields
    <fields.Field>` that you declare as class attributes and a class ``Meta``:

    .. class:: Meta

        Used to declare Django-SphinxQL related options.
        An index must always define the ``model`` of its Meta:

        .. attribute:: model

            The model of this index. E.g. ``model = blog.models.Post``.

        In case you want to index only particular instances, you can define the
        class attribute ``query``:

        .. attribute:: query

            Optional. The query Sphinx uses to index its data, e.g.
            ``query = models.Post.objects.filter(date__year__gt=2000)``. If not
            set, Django-SphinxQL uses ``.objects.all()``.

        .. _ranged-queries: http://sphinxsearch.com/docs/current.html#ranged-queries

        .. attribute:: range_step

            Optional. Defining it automatically enables ranged-queries_.
            This integer defines the number of rows per query retrieved during
            indexing. It increases the number of queries during indexing, but
            reduces the amount of data transfer for each query.

        In case you want to override Sphinx settings only to this particular
        index, you can also define the following class attributes:

        .. attribute:: source_params

            A dictionary of Sphinx options to override Sphinx settings of
            ``source`` for this particular index.

            See how to use in :ref:`override-settings`.

        .. attribute:: index_params

            A dictionary of Sphinx options to override Sphinx settings of
            ``index`` for this particular index.

            See how to use in :ref:`override-settings`.

Field
~~~~~

To identify a particular attribute of a Django model to be indexed,
Django-SphinxQL uses fields:

.. _attribute: http://sphinxsearch.com/docs/current.html#attributes
.. _search field: http://sphinxsearch.com/docs/current.html#fields

.. class:: fields.Field

    A field to be added to an :class:`~indexes.Index`. A field is always mapped
    to a Django model field, set on its initialization::

        my_indexed_text = FieldType('text')  # Index.Meta.model contains `text =
        ...`

    Currently it is not possible to use Django lookups on fields; we expect
    it to be possible in Django 1.8.

    Django-SphinxQL maps a field to a `search field`_ or a `attribute`_ of Sphinx:

    * attributes can be used to filter and order the results (
      :meth:`~sphinxql.query.SearchQuerySet.search_filter` and
      :meth:`~sphinxql.query.SearchQuerySet.search_order_by`).

    * search fields are indexed for text search, and thus can be used for textual
      searches with :meth:`~sphinxql.query.SearchQuerySet.search`. Sphinx **does**
      **not** store the original content of search fields.

    The following fields are currently implemented in Django-SphinxQL:

    * ``Text``: a search field (Sphinx equivalent ``sql_field_string``).
    * ``String``: (non-indexed) attribute for strings (``sql_attr_string``).
    * ``Date``: attribute for dates (``sql_attr_timestamp``).
    * ``DateTime``: attribute for datetimes (``sql_attr_timestamp``).
    * ``Float``: attribute for floats (``sql_attr_float``).
    * ``Bool``: attribute for booleans (``sql_attr_bool``).
    * ``Integer``: attribute for integers (``sql_attr_bigint``).

    .. _unix timestamp: https://en.wikipedia.org/wiki/Unix_time

    Note that Sphinx ``sql_attr_timestamp`` is stored as a `unix timestamp`_,
    so Django-SphinxQL only supports dates/times since to 1970.
