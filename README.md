[![Build Status](https://travis-ci.org/jorgecarleitao/django-sphinxql.svg?branch=master)](https://travis-ci.org/jorgecarleitao/django-sphinxql)

Django-SphinxQL implements [Sphinx search](sphinxsearch.com) for
[Django](djangoproject.com), thanks for checking it out.

Django is a Web framework for building websites with relational databases;
Sphinx is a search engine designed for relational databases.
Django-SphinxQL defines an ORM for using **Sphinx in Django**.
As corollary, it allows you to implement full text search with Sphinx in your
Django website.

Specifically, this API allows you to:

1. Configure Sphinx with Python.
2. Index Django models in Sphinx.
3. Execute Sphinx queries (SphinxQL) and automatically have the results as Django models.

All documentation is in the directory `docs` and [available online](http://django-sphinxql.readthedocs.org/en/latest/).

All tests are in the directory `tests`. To run them, use:

    PYTHONPATH=..:$PYTHONPATH django-admin.py test --settings=tests.settings_test tests

Django-SphinxQL requires:
- Python 3
- mysql or postgres
- latest Django
- latest Sphinx

Our testing matrix uses the latest Django, Sphinx 2.2.6, with two builds, mysql
and postgres. For more details, you can check directory `tests` and `.travis.yml`.

**This project is in alpha stage.**

Installation
------------

Django-SphinxQL has no requirements besides Django and Sphinx.
To install Sphinx, use:

    export VERSION=2.2.6
    wget http://sphinxsearch.com/files/sphinx-$VERSION-release.tar.gz
    tar -xf sphinx-$VERSION-release.tar.gz
    cd sphinx-$VERSION-release
    ./configure --prefix=$HOME --with-pgsql
    make
    make install

To install Django-SphinxQL, use:

    pip install git+https://github.com/jorgecarleitao/django-sphinxql.git

Minimal configuration
---------------------

1. add `sphinxql` to the ``INSTALLED_APPS`` (this only installs management commands);
2. add ``INDEXES`` to settings:

        INDEXES = {
            'path': os.path.join(BASE_DIR, '_index'),  # also do `mkdir _index`.
            'sphinx_path': BASE_DIR
        }

- ``path`` is where Sphinx database is going to be created
- ``sphinx_path`` is the directory that will contain Sphinx-specific files.

Index your models
-----------------

Assume you have a model ``Document`` with a ``summary``, a ``text`` and a
``number`` that you want to index. To index it, create a file ``indexes.py`` in 
your app with:

    from sphinxql import indexes, fields
    from myapp import models

    class DocumentIndex(indexes.Index):
        my_summary = fields.Text(model_attr='summary')
        my_text = fields.Text(model_attr='text')
        my_number = fields.Integer(model_attr='number')

        class Meta:
            model = models.Document

To index your indexes, run:

    python manage.py index_sphinx

At this moment you may notice that some files will be created in
``settings.INDEXES['path']``: Sphinx database is populated.

Then, start Sphinx (only has to be started once):

    python manage.py start_sphinx

(for the sake of reversibility, to stop Sphinx use ``python manage.py stop_sphinx``)

Search your indexes
-------------------

Django-SphinxQL defines a subclass of Django ``QuerySet``'s, that interfaces with
all Sphinx-related operations. ``SearchQuerySet`` *only adds functionality*: if you
don't use Sphinx-related, it behaves as a ``QuerySet``.

Sphinx has a dedicated syntax for text search that Django-SphinxQL also accepts:

    >>> q = SearchQuerySet(DocumentIndex).search('@my_text toys for babies')

This particular query returns ``Documents`` restricted to the ones where
"toys for babies" match in field ``my_text``, ordered by the most relevant match.
Once you perform it, it does the following:

1. hit Sphinx database and convert results to ``DocumentIndex`` instances;
2. hit Django database to retrieve the respective ``Document`` instances;
3. annotate ``Document`` instances with the respective ``DocumentIndex``
   instances (in attribute ``search_result``)
4. returns the ``Document`` instances.

Step 2. is done using ``.filter(pk__in=[...])``. The results are ordered by relevance
because there was no specific call of ``order_by``: if you set any ordering
in Django Query, it uses Django ordering (i.e. it overrides the default ordering
but not an explicit ordering). See docs for detailed information.

Known limitations
-----------------

* Only supports ``mysql`` and ``postgres`` backends (constraint on Sphinx engine)
* Does not allow to index data from lookups
* Null values are considered empty strings or 0 (constraint on Sphinx engine)
* Only supports dates and times since 1970 (constraint on Sphinx engine)
* Most Sphinx functionality *is not* implemented, notably real time indexes.
