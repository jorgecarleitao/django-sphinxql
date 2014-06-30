Indexes API
===========

.. currentmodule:: sphinxql

This document explains how Django-SphinxQL maps a Django model into a Sphinx
index::

    # indexes.py
    from sphinxql import fields, indexes
    from myapp import models

    class PostIndex(indexes.Index):
        text = fields.Text('text')  # Post has the model field ``text``
        date = fields.Date('added_date')
        other_text = fields.Text('summary')

        class Meta:
            model = models.Post

The basic unit for indexing data from your database is an :class:`~indexes.Index`,
a class very similar to a Django ``Model``.

Index
~~~~~

.. class:: indexes.Index

    :class:`~indexes.Index` is a ORM to Sphinx-index a Django Model. It works in a similar
    fashion to a Django model: you set up the :class:`fields <fields.Field>`, and
    it constructs an index out of these fields.

    .. class:: Meta

        An index has always a class ``Meta``. This class contains Django-SphinxQL
        specific data to not pollute the Index itself. The Meta must always define
        the attribute ``model``:

        .. attribute:: model

            The Django model, e.g. ``model = models.Post``

        In case you want to the index to particular instances you can use the
        attribute ``query``:

        .. attribute:: query

            Optional, the query it uses to index its data, e.g.
            ``query = models.Post.filter(year__gt=2000)``.

    Only the attributes of the ``Index`` that are :class:`fields <fields.Field>`
    are used by Django-SphinxQL.

    We recommend defining indexes in a ``indexes.py`` module, inside your app.

Field
~~~~~

To identify a particular Django model attribute to be indexed, Django-SphinxQL,
like Django, uses fields:

.. class:: fields.Field

    A field to be added to the Sphinx database. A field must always be mapped to
    a Django model field. This is done on its initialization::

        my_indexed_text = Field('text')  # Index.Meta.model contains `text = ...`

    There are two types of fields in Sphinx: attributes and indexed attributes.

    * Attributes are the equivalent to columns in relational databases.

    * Indexed attributes are attributes that are indexed for text search, and thus
      can also be used in textual searches.

    The following fields are implemented in Django-SphinxQL:

    * ``Text``: the only indexed attribute (Sphinx equivalent ``sql_field_string``).
    * ``String``: (non-indexed) attribute for strings (``sql_attr_string``).
    * ``Date``: attribute for dates (``sql_attr_timestamp``).
    * ``DateTime``: attribute for date times (``sql_attr_timestamp``).
    * ``Float``: attribute for floats (``sql_attr_float``).
    * ``Bool``: attribute for booleans (``sql_attr_bool``).

    .. _unix timestamp: https://en.wikipedia.org/wiki/Unix_time

    Sphinx ``sql_attr_timestamp`` is stored in `unix timestamp`_,
    so, currently, Django-SphinxQL only supports dates/time since to 1970.

    .. note::

        Sphinx is a new database: you should only use attributes when you are
        sure that you will require them e.g. for ordering or filtering results
        in the Sphinx database. Sphinx replicates data already persistent in your
        database.
