Guide
=====

How to index models
-------------------

Django has models and model fields, Django-SphinxQL has indexes and index fields.
Each index is associated with a model, and its fields with the models' fields.

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

How to search
-------------

.. _extented query syntax: http://sphinxsearch.com/docs/current.html#extended-syntax

Sphinx implements searches, using its `extented query syntax`_, that Django-SphinxQL
handles explicitly::

    >>> DocumentIndex.objects.search('hello | world')
    >>> DocumentIndex.objects.search('@(my_summary_index, my_text_index) hello world')

These queries perform a search in Sphinx and return the results as as Django QuerySet.

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
