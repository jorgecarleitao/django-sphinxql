Django-SphinxQL implements [Sphinx search](sphinxsearch.com) on Django ORM,
thanks for checking it out.

This API allows you to:

* fully customize Sphinx in Python.
* index Django models.
* full text search on indexed models.

All documentation is in the directory `docs` and [available online](http://django-sphinxql.readthedocs.org/en/latest/).

All tests are in the directory `tests`. To run them, use

    PYTHONPATH=..:$PYTHONPATH django-admin.py test --settings=tests.settings_test tests

This project is in pre-alpha.
