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

    :class:`~indexes.Index` is a ORM to Sphinx-index a Django Model. It works in
    a similar fashion to a Django model: you set up the :class:`fields
    <fields.Field>`, and it constructs an index out of these fields.

    Formally, when an index is declared, it is automatically registered in the
    :class:`~sphinxql.configuration.configurators.IndexConfigurator` to
    Django-SphinxQL configure Sphinx.

    An index is always composed by two components: a set of :class:`fields
    <fields.Field>` that you declare as class attributes and a class ``Meta``:

    .. class:: Meta

        Class used to declare Django-SphinxQL specifics to not pollute the
        :class:`~indexes.Index` itself.

        An index must always define the attribute ``model``:

        .. attribute:: model

            Django-SphinxQL always associates an Index to a Django model, and this
            is the entry point for this association.

            E.g. ``model = models.Post``.

        In case you want to index only particular instances, you can use the
        class attribute ``query``:

        .. attribute:: query

            Optional, the query Sphinx uses to index its data, e.g.
            ``query = models.Post.filter(date__year__gt=2000)``. If not set,
            Django-SphinxQL uses ``.objects.all()``.

Field
~~~~~

To identify a particular attribute of a Django model to be indexed,
Django-SphinxQL uses fields:

.. _attribute: http://sphinxsearch.com/docs/current.html#attributes
.. _search field: http://sphinxsearch.com/docs/current.html#fields

.. class:: fields.Field

    A field to be added to the Sphinx index. A field must always be mapped to
    a Django model field, set on its initialization::

        my_indexed_text = FieldType('text')  # Index.Meta.model contains `text =
        ...`

    Currently it is not possible to use Django lookups on fields, but we expect
    it to be possible in Django 1.8.

    Django-SphinxQL maps a field to a `search field`_ or a `attribute`_:

    * attributes are the equivalent to columns in relational databases and can
      be used in :meth:`~sphinxql.query.SearchQuerySet.search_filter` and
      :meth:`~sphinxql.query.SearchQuerySet.search_order_by`.

    * search fields are indexed for text search, and thus can be used for textual
      searches with :meth:`~sphinxql.query.SearchQuerySet.search`. Sphinx **does**
      **not store** the original content of fields.

    The following fields are currently implemented in Django-SphinxQL:

    * ``Text``: indexed attribute for strings (Sphinx equivalent ``sql_field_string``).
    * ``String``: (non-indexed) attribute for strings (``sql_attr_string``).
    * ``Date``: attribute for dates (``sql_attr_timestamp``).
    * ``DateTime``: attribute for date times (``sql_attr_timestamp``).
    * ``Float``: attribute for floats (``sql_attr_float``).
    * ``Bool``: attribute for booleans (``sql_attr_bool``).
    * ``Integer``: attribute for integers (``sql_attr_bigint``).

    .. _unix timestamp: https://en.wikipedia.org/wiki/Unix_time

    Not that Sphinx ``sql_attr_timestamp`` is stored as a `unix timestamp`_,
    so Django-SphinxQL only supports dates/times since to 1970.
