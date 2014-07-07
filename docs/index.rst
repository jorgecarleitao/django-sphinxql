Django-SphinxQL documentation
=============================

Django-SphinxQL is an API to use `sphinx search <http://sphinxsearch.com>`_
in `Django <http://djangoproject.com>`_. Thanks for checking it out.

Django is a Web framework for building websites with relational databases;
Sphinx is a search engine designed for relational databases.
Django-SphinxQL defines an ORM for using **Sphinx in Django**.
As corollary, it allows you to implement full text search with Sphinx in your
Django website.

Specifically, this API allows you to:

1. Configure Sphinx with Python.
2. Index Django models in Sphinx.
3. Execute Sphinx queries (SphinxQL) and automatically have the results as Django models.

.. warning::

    This app is under development and is still pre-alpha.

.. _`publicos.pt`: http://publicos.pt

.. note::

    Yet, it is tested and is being used on production by its maintainer at
    `publicos.pt`_.

.. toctree::
   :maxdepth: 2

   indexes
   queryset
   expression
   configuration

Installation
------------

.. _Sphinx: http://sphinxsearch.com/docs/current.html#installation

Django-SphinxQL has no requirements besides Django and `Sphinx`_.

To install Sphinx (locally or on a server)::

    wget http://sphinxsearch.com/files/sphinx-2.1.8-release.tar.gz
    tar -xf sphinx-2.1.8-release.tar.gz
    cd sphinx-2.1.8-release
    ./configure --prefix=$HOME
    make
    make install

To install Django-SphinxQL, use::

    pip install git+https://github.com/jorgecarleitao/django-sphinxql.git

and add it to the ``INSTALLED_APPS``. Django-SphinxQL does not define any model:
it only installs management commands.

Minimal configuration
---------------------

To configure Django-SphinxQL, add ``INDEXES`` to settings::

    INDEXES = {
        'path': os.path.join(BASE_DIR, '_index'),
        'sphinx_path': BASE_DIR
    }

* ``path`` is where the database is going to be created
* ``sphinx_path`` is the directory that will contain Sphinx-specific files.

Index your models
-----------------

Assume you have a model ``Document`` with a ``summary``, a ``text`` and a
``number``. To index it, first create a file ``indexes.py`` with::

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

At this moment you may notice that some files will be created in
``settings.INDEXES['path']``: Sphinx database is populated.

Then, start Sphinx (only has to be started once)::

    python manage.py start_sphinx

(for the sake of reversibility, to stop Sphinx use ``python manage.py stop_sphinx``)

Search your indexes
-------------------

Django-SphinxQL defines a subclass of Django ``QuerySet``'s,
:class:`~sphinxql.query.SearchQuerySet`, that interfaces with all Sphinx-related
operations. ``SearchQuerySet`` *only adds functionality*: if you don't use it,
it is a ``QuerySet``.

Sphinx has a dedicated syntax for text search and Django-SphinxQL accepts it::

    >>> q = SearchQuerySet(DocumentIndex).search('@my_text toys for babies')

This particular query returns ``Documents`` restricted to the ones where
"toys for babies" match in field ``my_text``, ordered by the most relevant match.
Once you perform it, it does the following:

1. hit Sphinx database and convert results to ``DocumentIndex`` instances;
2. hit Django database to retrieve the respective ``Document`` instances;
3. annotate ``Document`` instances with the respective ``DocumentIndex``
   instances (attribute ``search_result``)
4. returns ``Document`` instances.

Step 2. is done using ``.filter(pk__in=[...])``. The results are ordered by relevance
because there was no specific call of ``order_by``: if you set any ordering
in Django Query, it uses Django ordering (i.e. it overrides default ordering but
not explicit ordering). See :doc:`queryset` for more info.

Known limitations
-----------------

.. _14030: https://code.djangoproject.com/ticket/14030

* Only supports ``mysql`` and ``postgres`` backends (constraint on Sphinx engine)
* Does not allow to index data from lookups (constraint on Django ticket 14030_)
* Null values are considered empty strings or 0 (constraint on Sphinx engine)
* Only supports dates and times since 1970 (constraint on Sphinx engine)

.. note::

    Django-SphinxQL *is not* a plug-and-play app for search: *it is an API*
    that allows you to easily configure and use Sphinx in Django.
    You should check first if Django-Haystack suits your needs.

    The main motivation for this API is that I needed to have a search on
    "Open Data", which typically are very static datasets. Sphinx uses this
    assumption on its standard "plain" index, which this app also uses.

    I didn't created a backend for Django-Haystack because I already maintain
    the backend for Xapian and I didn't wanted to be stuck to the particular
    API of Django-Haystack.

    You can think of Django-SphinxQL as an **alternative** to Django's ``__search``
    lookup.
