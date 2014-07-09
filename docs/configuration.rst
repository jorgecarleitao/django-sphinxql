Sphinx Configuration
====================

.. currentmodule:: sphinxql.configuration

Configure Sphinx
----------------

.. warning::

    This part of the documentation requires a minimal understanding of Sphinx.

Running Sphinx requires a configuration file ``sphinx.conf`` normally
written by the user, that contains an arbitrary number of ``sources`` and
``indexes``, one ``indexer`` and one ``searchd``.

Django-SphinxQL provides an API to construct the ``sphinx.conf`` in Django:
once you run Django with an :doc:`index <indexes>`, it automatically generates
the ``sphinx.conf`` from your code, like Django builds a database when you run
``syncdb/migrate``.

Equivalently to Django,  the ``sources`` and ``indexes`` of ``sphinx.conf`` are
configured by an ORM (see :doc:`indexes`); ``indexer`` and ``searchd`` are
configured by settings from Django settings.

Like Django, Django-SphinxQL already ships a (conservative) default configuration
for Sphinx, (e.g. it automatically sets Sphinx to assume unicode).
Django-SphinxQL requires two settings to be defined:

* ``INDEXES['path']``: the path of the database (a directory)
* ``INDEXES['sphinx_path']``: the path for sphinx-related files (a directory)

For example::

    INDEXES = {
        'path': os.path.join(BASE_DIR, '_index'),
        'sphinx_path': BASE_DIR,
    }

.. note::

    a) The paths must exist; b) ``'path'`` will have *some*
       files inside. c) 'sphinx_path' will contain 3 files: ``searchd.pid``,
       ``searchd.log``, and ``sphinx.conf``.

Currently, Django-SphinxQL accepts 4 optional sets of parameters:

* ``INDEXES['searchd_params']``
* ``INDEXES['indexer_params']``
* ``INDEXES['index_params']``
* ``INDEXES['source_params']``

Each of them must be a dictionary that maps a Sphinx option (a Python string,
e.g. 'charset_table') to a string or a tuple, depending whether the Sphinx option
is single-valued or multi-valued.

.. note::

    The options are Sphinx options, they are too many to document here,
    check its documentation; Django-SphinxQL will warn you (violently) if
    some option is not correct.

Example::

    INDEXES = {
            ...
            # sets U+00E0 to be considered part of the alphabet (and not be
            # considered a word separator) on all indexes.
            'index_params': {
                    'charset_table': '0..9, A..Z->a..z, _, a..z, U+00E0'
            }
            ...
    }

``'index_params'`` and ``'source_params'`` are used on every index configured;
``'indexer_params'`` and ``'searchd_params'`` are used in the ``indexer`` and
``searchd`` of ``sphinx.conf``.

Configuration references (internal)
-----------------------------------

.. warning::

    This part of the documentation is for internal use and subject to change.

Index configurator
^^^^^^^^^^^^^^^^^^

.. currentmodule:: sphinxql.configuration.configurators

.. class:: IndexConfigurator

    Object representing a Sphinx configuration.

    This class has one entry point, :meth:`register`, called automatically when
    :class:`~sphinxql.indexes.Index` is defined. On registering an index,
    it gathers settings from three places:

    * Django ``settings``;
    * :class:`~sphinxql.fields.Field` of the index;
    * :class:`~sphinxql.indexes.Index.Meta` of the index.

    From ``django.settings``:

    * ``INDEXES['path']``: the directory where the database is created.
    * ``INDEXES['sphinx_path']``: the directory where sphinx-related files are created (e.g. ``sphinx.conf``)
    * ``INDEXES['indexer_params']``: a dictionary with additional parameters for
      the :class:`~configuration.configurations.IndexerConfiguration`.
    * ``INDEXES['searchd_params']``: a dictionary with additional parameters for
      the :class:`~configuration.configurations.SearchdConfiguration`.
    * ``INDEXES['source_params']``: a dictionary with additional parameters for
      the :class:`~configuration.configurations.SourceConfiguration`.
    * ``INDEXES['index_params']``: a dictionary with additional parameters for
      the :class:`~configuration.configurations.IndexConfiguration`.

    The set of available parameters can be found in Sphinx documentation.

    From each field, the configurator uses its ``type`` and ``model_attr``; from the
    :class:`~sphinxql.indexes.Index.Meta`, it uses:

    * :class:`~sphinxql.indexes.Index.Meta.model`: the Django model the index is respective to.
    * :class:`~sphinxql.indexes.Index.Meta.query`: the Django query the index is populated from.

source configuration
^^^^^^^^^^^^^^^^^^^^

.. currentmodule:: sphinxql.configuration.configurations

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

.. currentmodule:: sphinxql.configuration.configurations

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

.. currentmodule:: sphinxql.configuration.configurations

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

.. currentmodule:: sphinxql.configuration.configurations

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
