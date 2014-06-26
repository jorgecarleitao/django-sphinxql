Django-SphinxQL documentation
=============================

Django-SphinxQL is an API to use `sphinx search <http://sphinxsearch.com>`_
with `Django <http://djangoproject.com>`_. Thanks for checking it out.

Django is a Web framework for building websites with relational databases;
Sphinx is a search engine designed to be used in relational databases.
Django-SphinxQL defines an ORM for using **Sphinx within Django**.

As corollary, it allows you to implement full text search with Sphinx
in your Django website. Specifically, this API allows you to:

1. Configure Sphinx with Python.
2. Index Django models in Sphinx.
3. Execute Sphinx queries (SphinxQL) and retrieve the results like Django.

.. warning::

    This app is under development and its features are limited.

.. note::

    Yet, they are tested.

.. toctree::
   :maxdepth: 2

   howto
   indexes
   expression
   queryset
   configuration

Installation
------------

.. _Sphinx: http://sphinxsearch.com/docs/current.html#installation

Django-SphinxQL has no requirements besides Django and `Sphinx`_.

To install Django-SphinxQL, use::

    pip install git+https://github.com/jorgecarleitao/django-sphinxql.git

and add it to the ``INSTALLED_APPS``. Django-SphinxQL does not define any model:
it only installs management commands.

Minimal configuration
---------------------

To configure Django-SphinxQL, add ``INDEXES`` to settings::

    INDEXES = {
        'PATH': os.path.join(BASE_DIR, '_index'),
        'sphinx_path': BASE_DIR
    }

* ``PATH`` is where the database is going to be created
* ``sphinx_path`` is the directory that will contain Sphinx-specific files.

Index your models
-----------------

You have a model ``Document`` with a ``summary``, a ``text`` and a ``number``.
To index it, first create a file ``indexes.py`` with::

    from sphinxql import indexes, fields
    from myapp import models

    class DocumentIndex(indexes.Index):
        my_summary = fields.Text(model_attr='summary')
        my_text = fields.Text(model_attr='text')
        my_number = fields.Integer(model_attr='number')

        class Meta:
            model = models.Document

Then run::

    python manage.py index_sphinx

This runs the query ``Document.objects.all()`` against your database,
picking the data and indexing it. At this moment you may notice that some files
will be created in ``settings.INDEXES['PATH']``: Sphinx database is populated.

Then, start Sphinx (only have to be started once)::

    python manage.py start_sphinx

(for the sake of reversibility, to stop Sphinx use ``python manage.py stop_sphinx``)

Search your indexes
-------------------

Sphinx uses two syntaxes: a dialect of SQL for ordering, filtering and
aggregation - SphinxQL -, and an Sphinx-specific ``extended query syntax`` (EQS)
for text search.

SQL filter
^^^^^^^^^^

The interface of Django-SphinxQL is close to Django, but without lookups::

    >>> from sphinx.sql import C
    >>> q = DocumentIndex.objects.filter(C('my_number') > 2)
    >>> isinstance(q[0], Document)  # True

All Python operators are overridden in ``C`` such that ``C('my_number') > 2``
is interpreted in SQL as ``WHERE my_number > 2``. You can write::

    >>> DocumentIndex.objects.filter(C('my_number') + 2 > 2)

The only exception is the Python operator ``|``. This is used to create
operators that are defined in SQL but are not defined or cannot be overridden
in Python, such as ``IN`` and ``BETWEEN``::

    >>> from sphinxql.sql import C, In, And
    >>> e = C('my_number') |In| (2, 3, 4)
    >>> e = (C('my_number') > 2) |And| e
    >>> DocumentIndex.objects.filter(e)

Like in Django, these queries are lazy and cached. Once you perform it,
it does the following:

1. converts itself to SphinxQL;
2. hit Sphinx database with that expression;
3. convert results to ``DocumentIndex`` instances;
4. hit Django database to retrieve the respective ``Document`` instances;
5. annotate ``Document`` instances with the respective ``DocumentIndex`` instances;
6. returns ``Document`` instances.

Specifically, the query is lazy in respect to point 2; once it is executed, it
performs two hits, one on each database.

You can customize Django's queryset (e.g. for annotation) using ``queryset``::

    q = DocumentIndex.objects.filter(sphinx_filtering)
    q.queryset = q.queryset.filter(django_filtering)

You can only perform operations on the ``queryset`` that still return a query.

 * If an object is filtered out by any query, it is excluded.
 * If an ordering is given in Sphinx, Django ordering is ignored.

text search
^^^^^^^^^^^

.. _EQS: http://sphinxsearch.com/docs/current.html#extended-syntax

SphinxQL has a reserved keyword ``MATCH`` to implement textual searches.
A textual search always performs two distinct operations: 1. filter results,
2. attribute weights to results::

    >>> q = DocumentIndex.objects.match('@my_text toys for babies')
    >>> isinstance(q[0], Document)  # True

The syntax for ``match`` is described in Sphinx documentation for EQS_.
Unless there is an order already defined, the results are ordered
according to relevance given by the match.

Current limitations with Django
-------------------------------

* Only supports ``mysql`` and ``postgres`` backends (constraint of Sphinx engine)
* Does not allow to index data from lookups
* Null values are considered empty strings or 0 (constraint of Sphinx engine)
* Only supports dates and times since 1970 (constraint of Sphinx engine)

.. _author note:

Author's note
-------------

Django-SphinxQL currently uses its own SQL expression API and QuerySets.
However, Django 1.7/1.8 plans an API to allow custom lookup expressions and custom
SQL expressions. Once this API is established, we may try to migrate to it.
