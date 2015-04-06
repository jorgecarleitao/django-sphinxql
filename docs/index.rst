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
3. Execute Sphinx queries (SphinxQL) and have the results in Django.

Check README for a quick overview of how to quickly get it working. Check this
documentation for a detailed explanation of everything that is available in
Django-Sphinxql.

.. toctree::
   :maxdepth: 2

   indexes
   queryset
   expression
   configuration
