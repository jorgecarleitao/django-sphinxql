Indexes API
===========

.. currentmodule:: sphinxql

This document explains how Django-SphinxQL maps a Django model into a Sphinx
index.

Sphinx
------

Sphinx uses a SQL query to retrieve data from a relational database to index
it. This means that Django-SphinxQL must know:

1. what you want to index (e.g. what data)
2. how you want to index (e.g. type)

to pass a SQL query, built in Django, to Sphinx. In the same spirit of Django,
Django-SphinxQL defines an ORM for performing these two operations::

    # indexes.py
    from sphinxql import fields, indexes
    from myapp import models

    class PostIndex(indexes.Index):
        text = fields.Text('text')  # Post has the model field ``text``
        date = fields.Date('added_date')
        summary = fields.Text('summary')

        class Meta:
            model = models.Post  # the model we are indexing

The ``fields`` and the ``Meta.model`` identify "what"; the specific field, e.g.
``Text``, identifies "how". Currently, Django-SphinxQL does not type check
if the fields in the ``Model`` can be represented by the specific Django-SphinxQL
fields.

Index
~~~~~

.. class:: indexes.Index

    :class:`~indexes.Index` is a ORM to Sphinx-index a Django Model. It works in
    a similar fashion to a Django model: you set up the :class:`fields
    <fields.Field>`, and it constructs an index out of these fields.

    An index has always a class ``Meta``:

    .. class:: Meta

        This class contains Django-SphinxQL specific data to not pollute the
        :class:`~indexes.Index` itself. The Meta must always define the
        attribute ``model``:

        .. attribute:: model

            The Django model, e.g. ``model = models.Post``.

        In case you want to index only particular instances you can use the
        attribute ``query``:

        .. attribute:: query

            Optional, the query it uses to index its data, e.g.
            ``query = models.Post.filter(year__gt=2000)``.
            If not set, Django-SphinxQL uses ``Model.objects.all()``.

    We recommend defining indexes in a ``indexes.py`` module, inside your app.

    When an ``Index`` is defined, it is automatically registered in the
    :class:`~sphinxql.configurations.configurator.IndexConfigurator`.

Field
~~~~~

To identify a particular Django model attribute to be indexed, Django-SphinxQL
uses fields:

.. class:: fields.Field

    A field to be added to the Sphinx index. A field must always be mapped to
    a Django model field, set on its initialization::

        my_indexed_text = Field('text')  # Index.Meta.model contains `text = ...`

    Currently it is not possible to map a field to a Django lookup expression, but
    we expect it to be possible in Django 1.8.

    There are two types of fields in Sphinx: attributes and indexed attributes:

    * Attributes are the equivalent to columns in relational databases and can
      be used in :meth:`Sphinxql.query.SearchQuerySet.search_filter`.

    * Indexed attributes are attributes that are indexed for text search, and thus
      can also be used for textual searches in
      :meth:`Sphinxql.query.SearchQuerySet.search`.

    The following fields are implemented in Django-SphinxQL:

    * ``Text``: indexed attribute for strings (Sphinx equivalent ``sql_field_string``).
    * ``String``: (non-indexed) attribute for strings (``sql_attr_string``).
    * ``Date``: attribute for dates (``sql_attr_timestamp``).
    * ``DateTime``: attribute for date times (``sql_attr_timestamp``).
    * ``Float``: attribute for floats (``sql_attr_float``).
    * ``Bool``: attribute for booleans (``sql_attr_bool``).
    * ``Integer``: attribute for integers (``sql_attr_bigint``).

    .. _unix timestamp: https://en.wikipedia.org/wiki/Unix_time

    Sphinx ``sql_attr_timestamp`` is stored in `unix timestamp`_,
    so, currently, Django-SphinxQL only supports dates/time since to 1970.
