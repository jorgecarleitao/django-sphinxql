Guide
=====

How to index models
-------------------

Django has models and model fields, Django-SphinxQL has
indexes and index fields. One index is only associated with a model, and its
fields with the models' fields.

Consider::

    class Document(models.Model):
        summary = models.CharField(max_length=254)
        text = models.TextField()
        number = models.Integer()

To build an index, in ``indexes.py``, define::

    from sphinxql import indexes, fields

    class DocumentIndex(indexes.Index):
        my_summary_index = fields.Text('summary')
        my_text_index = fields.Text('text')
        number = fields.Integer('number)

        class Meta:
            model = models.Document

When Django starts, Django-SphinxQL recognizes the index and transforms it into
a ``sphinx.conf`` file, which is used by Sphinx. To index the database, use::

    >>> python manage.py index_sphinx

You should run this command every time you want reindex your data (e.g.
using a schedule to reindex the data).

.. note::

    Sphinx does have real time indexing and there are plans to support it in
    Django-SphinxQL.

How to filter
-------------

.. _Inflix: http://code.activestate.com/recipes/384122-infix-operators/

By filter we refer to any operation that does not involve textual matches,
such conditions on ``DocumentIndex.number``.

Django-SphinxQL borrows ideas from Django, with a slightly different syntax::

    >>> from sphinxql.sql import C
    >>> q = DocumentIndex.objects.search_filter(C('number') > 2)

I.e. Django-SphinxQL does not support lookups, and implements conditions
directly in Python. It currently supports:

    * All comparisons (e.g. ``>``, ``!=``)
    * All standard math operations (e.g. ``+``, ``**``)
    * Does not implement bitwises (``|``, ``&`` or ``^``)
    * boolean negation is done with ``~``
    * negation is done with ``-``

Django-SphinxQL also implements operators that cannot be represented or overridden
in Python using Inflix_::

    >>> from sphinxql.sql import In, Between, And
    >>> from datetime import date
    >>> e = C('number') |In| [2, 3, 4, 5]
    >>> e1 = C('date') |Between| (date(2014, 1, 1), date(2014, 2, 1))
    >>> q = DocumentIndex.objects.search_filter(e |And| e1)

Dates and times work as in Django: ``USE_TZ`` and ``TIME_ZONE`` are supported.
Care must taken since Sphinx represents times in a unix timestamp, that is
restricted to 1970 - 2038. Outside this range, it is unexpected behavior.

How to search
-------------

.. _extented query syntax: http://sphinxsearch.com/docs/current.html#extended-syntax

By search we refer to the operation of querying textual information to obtain
a set of objects and respective relevance to the query.
Sphinx implements searches, restricted to **indexed attributes**, using
its `extented query syntax`_, that Django-SphinxQL handles explicitly::

    >>> DocumentIndex.objects.search('hello | world')
    >>> DocumentIndex.objects.search('@(my_summary_index, my_text_index) hello world')

Successive ``search`` join the final query, i.e.::

    >>> DocumentIndex.objects.search('hello').search('world')

is equivalent to::

    >>> DocumentIndex.objects.search('hello world')

because there can only be one ``search`` per query in Sphinx.

How to sort
-----------

By default, results are sorted by Django ``id`` if there is no ``search`` call,
and by relevance if there is a ``search``. If you want to use other
sorting, e.g. by attributes, use the function ``search_order_by()``::

    >>> DocumentIndex.objects.search('hello world').search_order_by(C('number'), -C('date))

Sorting currently only supports single columns (i.e. no expressions). Django's
``id`` is ``C('@id')`` and the search relevance (when ``search`` is used), is
``C('@relevance')``.

Results format
--------------

The results are a list of Django models instances of the ``DocumentIndex``::

    >>> q = DocumentIndex.objects.search('hello world').search_order_by(C('number'), -C('date))
    >>> assert isinstance(q[0], Document)
    >>> assert isinstance(q[0].search_result, DocumentIndex)

Notice that ``q[...]`` does not return a Django queryset: you cannot continue to
filter or order it since Django database has no information about the particular
ordering Sphinx proposes. The model instances come annotated with a
``search_result`` populated with the attributes retrieved from Sphinx.
