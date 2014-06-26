Sphinx Configuration
====================

.. currentmodule:: configuration

Running Sphinx requires a Sphinx configuration file, ``sphinx.conf``,
that configures Sphinx. It consists of a set of ``source``s, ``index``es, an
``indexer``, and a ``searchd``.

Django-SphinxQL provides an API to construct the file from your Python code.
The main item of this API is the :class:`Index`, that defines an ORM for Sphinx.

When an :class:`Index` is defined, it is registered in a :class:`IndexConfigurator`
that is responsible to translate it to ``sphinx.conf``.

:class:`Index` only contains part of the configuration; this document introduces
how you can introduce any configuration to Sphinx.


Index configurator
^^^^^^^^^^^^^^^^^^

.. currentmodule:: configuration.configurators

.. class:: IndexConfigurator

    Django-SphinxQL uses this class to build and output ``sphinx.conf``.

    It has one entry point :meth:`register`, called automatically when :class:`~sphinxql.indexes.Index`
    is defined. On registering an index, it gathers information from three places:

    * Django ``settings``.
    * :class:`~sphinxql.fields.Field` of the index
    * :class:`~sphinxql.indexes.Index.Meta` of the index

    From ``django.settings``, it uses the following information:

    * ``INDEXES.PATH``: The directory where the database is created.
    * ``INDEXES.sphinx_path``: The directory where sphinx-related files are created (e.g. ``sphinx.conf``)
    * ``INDEXES.indexer_params``: a dictionary with additional parameters for the :class:`IndexerConfiguration`.
    * ``INDEXES.searchd_params``: a dictionary with additional parameters for the :class:`SearchdConfiguration`.
    * ``INDEXES.source_params``: a dictionary with additional parameters for the :class:`SourceConfiguration`.
    * ``INDEXES.index_params``: a dictionary with additional parameters for the :class:`IndexConfiguration`.

    From the fields, it uses its ``type`` and ``model_attr`` and from the Meta, it uses:

    * ``model``: the Django model the index is respective to
    * ``model``: the Django model the field is


source configuration
^^^^^^^^^^^^^^^^^^^^

.. currentmodule:: configuration.configurations

.. _source configuration options: http://sphinxsearch.com/docs/current.html#confgroup-source

.. class:: SourceConfiguration(params)

    A class that can represent itself as an ``source`` of ``sphinx.conf``.

    It contains the parameters of the ``source``. The argument of this
    class must be a dictionary mapping parameters to values.

    This class always validates the parameters, raising an ``ImproperlyConfigured``
    if any is wrong. The valid parameters are documented in Sphinx
    `source configuration options`_.

    It has one public method:

    .. method:: format_output

        Returns a string with the parameters formatted according to
        the ``sphinx.conf`` syntax.

index configuration
^^^^^^^^^^^^^^^^^^^

.. currentmodule:: configuration.configurations

.. _index configuration options: http://sphinxsearch.com/docs/current.html#confgroup-index

.. class:: IndexConfiguration(params)

    A class that can represent itself as an ``index`` of ``sphinx.conf``.

    It contains the parameters of the ``index``. The argument of this
    class must be a dictionary mapping parameters to values.

    This class always validates the parameters, raising an ``ImproperlyConfigured``
    if any is wrong. The valid parameters are documented in Sphinx
    `index configuration options`_.

    It has one public method:

    .. method:: format_output

        Returns a string with the parameters formatted according to
        the ``sphinx.conf`` syntax.

indexer configuration
^^^^^^^^^^^^^^^^^^^^^

.. currentmodule:: configuration.configurations

.. _indexer configuration options: http://sphinxsearch.com/docs/current.html#confgroup-indexer

.. class:: IndexerConfiguration(params)

    A class that can represent itself as an ``indexer`` of ``sphinx.conf``.

    It contains the parameters of the ``indexer``. The argument of this
    class must be a dictionary mapping parameters to values.

    This class always validates the parameters, raising an ``ImproperlyConfigured``
    if any is wrong. The valid parameters are documented in Sphinx
    `indexer configuration options`_.

    It has one public method:

    .. method:: format_output

        Returns a string with the parameters formatted according to
        the ``sphinx.conf`` syntax.


searchd configuration
^^^^^^^^^^^^^^^^^^^^^

.. currentmodule:: configuration.configurations

.. _searchd configuration options: http://sphinxsearch.com/docs/current.html#confgroup-searchd

.. class:: SearchdConfiguration(params)

    A class that can represent itself as the ``searchd`` of ``sphinx.conf``.

    It contains the parameters of the ``searchd``. The argument of this
    class must be a dictionary mapping parameters to values.

    This class always validates the parameters, raising an ``ImproperlyConfigured``
    if any is wrong. The valid parameters are documented in Sphinx
    `searchd configuration options`_.

    It has one public method:

    .. method:: format_output

        Returns a string with the parameters formatted according to
        the ``sphinx.conf`` syntax.
