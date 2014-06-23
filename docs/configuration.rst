Sphinx Configuration
====================

.. currentmodule:: configuration

Sphinx configuration file, ``sphinx.conf``, consists of a set of ``source``s,
``index``es, an ``indexer``, and a ``searchd``.

Django-SphinxQL uses a ``Configurator`` to construct these items and output a
``sphinx.conf``. So, the Python code *defines* the ``sphinx.conf``.

While Sphinx allows to use different sources to a given index, Django-SphinxQL
uses one source per index (which we denote from now on as ``index``).

This is done using an :class:`Index`: a class that maps models from an ORM to data
structures of Sphinx.

These indexes are registered in to a :class:`IndexConfigurator`
that is responsible to translate them to ``sphinx.conf`` syntax.

Index configurator
^^^^^^^^^^^^^^^^^^

.. currentmodule:: configuration.configurators

.. class:: IndexConfigurator

    Django-SphinxQL uses this class to build and output ``sphinx.conf``.
    It gathers information from the following places:

    * Django ``settings``.
    * the :class:`indexes.Index`es defined in the different installed apps, in particular from their:
      * :class:`fields`
      * :class:`indexes.Index.Meta`

    From ``django.settings``, it uses the following information:

    * ``INDEXES.PATH``: The directory where the database is created.
    * ``INDEXES.sphinx_path``: The directory where sphinx-related files are created.
    * ``INDEXES.indexer_params``: a dictionary with additional parameters for the :class:`IndexerConfiguration`.
    * ``INDEXES.searchd_params``: a dictionary with additional parameters for the :class:`SearchdConfiguration`.
    * ``INDEXES.source_params``: a dictionary with additional parameters for the :class:`SourceConfiguration`.
    * ``INDEXES.index_params``: a dictionary with additional parameters for the :class:`IndexConfiguration`.

    From the fields, it uses its type, and from the Meta, the following is allowed


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
