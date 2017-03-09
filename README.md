[![Build Status](https://travis-ci.org/jorgecarleitao/django-sphinxql.svg?branch=master)](https://travis-ci.org/jorgecarleitao/django-sphinxql)
[![Coverage Status](https://coveralls.io/repos/jorgecarleitao/django-sphinxql/badge.svg?branch=master&service=github)](https://coveralls.io/github/jorgecarleitao/django-sphinxql?branch=master)

Django-SphinxQL implements [Sphinx search](http://sphinxsearch.com) for
[Django](https://www.djangoproject.com), thanks for checking it out.

Django is a Web framework for building websites with relational databases;
Sphinx is a search engine designed for relational databases.
Django-SphinxQL defines an ORM for using **Sphinx in Django**.
As corollary, it allows you to implement full text search with Sphinx in your
Django website.

Specifically, this API allows you to:

1. Configure Sphinx with Python.
2. Index Django models in Sphinx.
3. Execute Sphinx queries (SphinxQL) using Django-like expressions and have the 
results as Django models.

Django-SphinxQL requires:

- Python 3
- pymysql
- Django (>=1.8)
- Sphinx
- A backend (pymysql or psycopg2)

Our build matrix in Travis has 8 builds:

- Python 3.4
- Django 1.8 and 1.10
- Sphinx 2.2.10 and 2.2.11
- mysql and postgres backends

For more details, you can check the directory `tests` and `.travis.yml`.

To run the tests locally, use:

    PYTHONPATH=..:$PYTHONPATH django-admin.py test --settings=tests.settings_test tests

The next sections present a minimal setup to use this package. The full documentation
is available [here](http://django-sphinxql.readthedocs.org/en/latest/).

Installation
------------

Django-SphinxQL has no requirements besides Django and Sphinx. To install Sphinx,
use:

    export VERSION=2.2.10
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

Django-SphinxQL requires a directory to store its database and be registered as
installed app (it doesn't contain Django models):

1. add `sphinxql` to the ``INSTALLED_APPS``;
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

`model_attr` can be either a string with lookups or an [F expression](https://docs.djangoproject.com/en/1.8/topics/db/queries/#using-f-expressions-in-filters).
E.g. `type_name = fields.Text(model_attr='type__name')` will index the name of
the ForeignKey `type` of your model, while 

    type_name = fields.Text(model_attr=Concat('type__name', Value(' '),
                                              'my_text',
                                              output_field=CharField()))

indexes the concatenation of two fields (see also [Django documentation](https://docs.djangoproject.com/en/dev/ref/models/database-functions/#concat)).
In principle the index fields accept any Django expression Django annotate accepts.

To index your indexes, run:

    python manage.py index_sphinx

At this moment you may notice that some files will be created in
``settings.INDEXES['path']``: Sphinx database is populated.

Then, start Sphinx daemon (only has to be started once):

    python manage.py start_sphinx

(for the sake of reversibility, to stop Sphinx use ``python manage.py stop_sphinx``)

Search your indexes
-------------------

Django-SphinxQL defines a subclass of Django ``QuerySet``'s, that interfaces with
all Sphinx-related operations. ``SearchQuerySet`` *only adds functionality*: if you
don't use Sphinx-related, it is a ``QuerySet``.

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

* Null values are considered empty strings or 0 (constraint on Sphinx engine)
* Only supports dates and times since 1970 (constraint on Sphinx engine)
* Most Sphinx functionality *is not* implemented, notably real time indexes.

Final note
----------

You should check if [Django-Haystack](http://haystacksearch.org/) suits your needs.

Django-SphinxQL is useful when you can index your data on a time-scale
different from "real time". It should be much faster in indexing, and it should
have lower memory requirements.
