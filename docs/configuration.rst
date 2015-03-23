Sphinx Configuration
====================

.. currentmodule:: sphinxql.configuration

Configure Sphinx
----------------

.. note::

    This part of the documentation requires a minimal understanding of Sphinx.

Running Sphinx requires a configuration file ``sphinx.conf``, normally
written by the user, that contains an arbitrary number of ``sources`` and
``indexes``, one ``indexer`` and one ``searchd``.

Django-SphinxQL provides an API to construct the ``sphinx.conf`` in Django:
once you run Django with an :class:`~sphinxql.indexes.Index`,
it automatically generates the ``sphinx.conf`` from your code, like Django builds
a database when you run ``migrate``.

.. note::

    The ``sphinx.conf`` is modified by Django-SphinxQL from your code. It
    doesn't need to be added to the version control system.

Equivalently to Django, the ``sources`` and ``indexes`` of ``sphinx.conf`` are
configured by an ORM (see :doc:`indexes`); ``indexer`` and ``searchd`` are
configured by settings in Django settings.

Django-SphinxQL requires the user to define two settings:

* ``INDEXES['path']``: the path of the database (a directory)
* ``INDEXES['sphinx_path']``: the path for sphinx-related files (a directory)

For example::

    INDEXES = {
        'path': os.path.join(BASE_DIR, '_index'),
        'sphinx_path': BASE_DIR,
    }

.. note::

    a) The paths must exist; b) ``'path'`` will contain the Sphinx database.
    c) 'sphinx_path' will contain 3 files:
        ``pid file``, ``searchd.log``, and ``sphinx.conf``.

Like Django, Django-SphinxQL already provides a (conservative) default
configuration for Sphinx (e.g. it automatically sets Sphinx to assume unicode).

Default settings
^^^^^^^^^^^^^^^^

Django-SphinxQL uses the following default settings::

    'index_params': {
        'type': 'plain',
        'charset_type': 'utf-8'
    }
    'searchd_params': {
        'listen': '9306:mysql41',
        'pid_file': os.path.join(INDEXES['sphinx_path'], 'searchd.pid')
    }

.. _override-settings:

Defining and overriding settings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Django-SphinxQL applies settings in cascade, overriding previous settings if
necessary, in the following order:

1. first, it uses Django-SphinxQL's default settings
2. them, it applies settings of ``settings.INDEXES``, possibly overriding some
   settings in 1.
3. finally, it applies the settings defined in the :class:`Index.Meta
   <sphinxql.indexes.Index.Meta>` to that specific index, possibly overriding
   settings in 2.

The project-wise settings use:

* ``settings.INDEXES['searchd_params']``
* ``settings.INDEXES['indexer_params']``
* ``settings.INDEXES['index_params']``
* ``settings.INDEXES['source_params']``

Each of them must be a dictionary that maps a Sphinx option (a Python string,
e.g. ``'charset_table'``) to a string or a tuple, depending whether the Sphinx
option is single-valued or multi-valued.

For example::

    INDEXES = {
            ...
            # sets U+00E0 to be considered part of the alphabet (and not be
            # considered a word separator) on all registered indexes.
            'index_params': {
                'charset_table': '0..9, A..Z->a..z, _, a..z, U+00E0'
            }
            # additionally to default, turns off query cache (see Sphinx docs)
            'source_params': {
                'sql_query_pre': ('SET SESSION query_cache_type=OFF',)
            }
            ...
    }

.. _Sphinx documentation: http://sphinxsearch.com/docs/current.html#conf-reference

You can also override settings of ``source`` and ``index`` only for a particular
index by defining :attr:`~sphinxql.indexes.Index.Meta.source_params` and
:attr:`~sphinxql.indexes.Index.Meta.index_params`.

.. note::

    The options must be valid Sphinx options as defined in `Sphinx documentation`_.
    Django-SphinxQL warns you if some option is not correct or is not valid.

``'index_params'`` and ``'source_params'`` are used on every index configured;
``'indexer_params'`` and ``'searchd_params'`` are used in the ``indexer`` and
``searchd`` of ``sphinx.conf``.

Configuration references (internal)
-----------------------------------

.. warning::

    This part of the documentation is for internal use and subject to change.

Index configurator
^^^^^^^^^^^^^^^^^^

.. class:: configurators.IndexConfigurator

    This class is declared only once in Django-Sphinxql, and is responsible for
    mapping your :class:`indexes <sphinxql.indexes.Index>` into a sphinx
    ``sphinx.conf``.

    This class has one entry point, :meth:`register`, called automatically when
    :class:`~sphinxql.indexes.Index` is defined.

    .. method:: register(index)

        Registers an :class:`~sphinxql.indexes.Index` in the configuration.

        This is the entry point of this class to configure a new ``Index``.
        A declaration of an ``Index`` automatically calls this method to register
        itself.

        This method builds the source configuration and index configuration for
        the ``index`` and outputs the updated ``sphinx.conf`` to
        ``INDEXES['sphinx_path']``.

    On registering an index, :meth:`register` gathers settings from three places:

    * Django ``settings``;
    * :class:`~sphinxql.fields.Field` of the index;
    * :class:`~sphinxql.indexes.Index.Meta` of the index.

    From ``django.settings``:

    * ``INDEXES['path']``: the directory where the database is created.
    * ``INDEXES['sphinx_path']``: the directory for sphinx-related files.
    * ``INDEXES['indexer_params']``: a dictionary with additional parameters for
      the :class:`~configurations.IndexerConfiguration`.
    * ``INDEXES['searchd_params']``: a dictionary with additional parameters for
      the :class:`~configurations.SearchdConfiguration`.
    * ``INDEXES['source_params']``: a dictionary with additional parameters for
      the :class:`~configurations.SourceConfiguration`.
    * ``INDEXES['index_params']``: a dictionary with additional parameters for
      the :class:`~configurations.IndexConfiguration`.

    The set of available parameters can be found in Sphinx documentation.

    From each field, the configurator uses its ``type`` and ``model_attr``; from the
    :class:`~sphinxql.indexes.Index.Meta`, it uses:

    * :class:`~sphinxql.indexes.Index.Meta.model`: the Django model the index is respective to.
    * :class:`~sphinxql.indexes.Index.Meta.query`: the Django query the index is populated from.
    * :class:`~sphinxql.indexes.Index.Meta.range_step`: the step for ranged queries (see Sphinx docs)

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
