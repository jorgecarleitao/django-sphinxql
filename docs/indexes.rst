Indexes API
===========

.. currentmodule:: sphinxql

This document explains how Django-SphinxQL translates
a Python class into a Sphinx index, and how you can use it.

For those in a hurry, here's the code::

    from sphinxql import fields, indexes
    from myapp import models

    class PostIndex(indexes.Index):
        text = fields.Text('text')  # Post has the model field ``text``

        class Meta:
            model = models.Post

The basic unit for indexing data from your database is an :class:`~indexes.Index`,
a class very similar to a Django ``Model``.

Index
~~~~~

.. class:: indexes.Index

    Index is a ORM to text-index a Django Model.
    It works in a similar fashion to a Django model: you set up
    the fields, and it constructs an index out of these :class:`fields <fields.Field>`.

    .. class:: Meta

        An index has always a class ``Meta`` that points to the Django
        model it uses.

        .. attribute:: model

            The Django model, e.g. ``model = models.Post``

        .. attribute:: query

            Optional, the query it uses to index its data, e.g.
            ``query = models.Post.filter(year__gt=2000)``.

    Only the attributes of the ``Index`` that are :class:`Field` are indexed

    Technically, the indexes can be in any place; we recommend using ``indexes.py``.

Field
~~~~~

.. class:: fields.Field

    A field to be added to the Sphinx database.
    A field must always be mapped to a model field belonging to the
    Index the field belongs.

    There are two types of fields in Sphinx: attributes and indexed attributes.

    * Attributes are the equivalent to columns in relational databases in the sense
      that you can use SphinxQL to interact with them.

    * Indexed attributes are attributes that are indexed for text search, and thus
      can also be used in textual searches.

    The following fields are implemented in Django-SphinxQL:

    * ``Text``: indexed attribute for strings (Sphinx equivalent to ``sql_field_string``).
    * ``String``: attribute for strings (``sql_attr_string``).
    * ``Date``: attribute for dates (``sql_attr_timestamp``).
    * ``DateTime``: attribute for date times (``sql_attr_timestamp``).
    * ``Float``: attribute for floats (``sql_attr_float``).
    * ``Bool``: attribute for booleans (``sql_attr_bool``).

    .. _unix timestamp: https://en.wikipedia.org/wiki/Unix_time

    Sphinx ``sql_attr_timestamp`` is stored in `unix timestamp`_,
    i.e. it fails to index dates before 1970 properly.

    .. note::

        Sphinx is a new database: you should only use attributes
        when you are sure that you will require them e.g. for ordering or
        filtering results in the Sphinx database. Sphinx replicates data already
        persistent in your database.
