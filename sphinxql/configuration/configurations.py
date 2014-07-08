from . import constants
from ..exceptions import ImproperlyConfigured


class Configuration(object):
    """
    A generic Sphinx configuration.

    Has a type, a type_name and parameters in a dictionary form.
    """
    type_name = None
    valid_parameters = tuple()
    mandatory_parameters = tuple()
    multi_valued_parameters = tuple()

    def __init__(self, name, params, parent=None):
        self.validate_parameters(params)

        self.name = name
        self.params = params
        self.parent = parent

    def _format_params(self):
        params_format = ''
        for param_name in self.params:
            param_values = self.params[param_name]
            # if is not multi-valued, is a list with 1 item.
            if not isinstance(param_values, (list, tuple)):
                param_values = [param_values]

            for param_value in param_values:
                params_format += '    %(param_name)s = %(param_value)s\n' % \
                                 {'param_name': param_name,
                                  'param_value': param_value}
        return params_format

    def _format_parent(self):
        """
        Formats configuration parent, if any.
        """
        if self.parent:
            return ': %(parent_name)s'.format({'parent_name': self.parent})
        else:
            return ''

    def format_output(self):
        """
        Formats this configuration into a string ready for sphinx.conf.
        """
        if not self.params:
            return ''

        return '%(type_name)s %(name)s %(parent_format)s\n{\n%(params_format)s}\n' % \
               {'type_name': self.type_name,
                'name': self.name,
                'parent_format': self._format_parent(),
                'params_format': self._format_params()}

    @classmethod
    def validate_parameters(cls, params):
        """
        Checks that all parameters `params` are valid for this configuration.
        """
        missing_parameters = set(cls.mandatory_parameters)

        for param_name in params:
            # check if it is valid.
            if param_name not in cls.valid_parameters:
                raise ImproperlyConfigured(
                    'Invalid parameter "{0}" for {1}. '
                    'See Sphinx documentation for "{1} configuration".'
                    .format(param_name, cls.type_name))

            # check if it is mandatory.
            if param_name in missing_parameters:
                missing_parameters.remove(param_name)

            # check if it is correctly typed.
            if param_name in cls.multi_valued_parameters:
                valid_types = (str, int, list, tuple)
            else:
                valid_types = (str, int)

            if not isinstance(params[param_name], valid_types):
                raise ImproperlyConfigured(
                    'Parameter "{0}" in {1} must be instance of '
                    '{2}.'.format(param_name, cls.type_name, valid_types))

            # check if each entry of the iterable is correctly typed.
            if isinstance(params[param_name], (list, tuple)):
                for entry in params[param_name]:
                    if not isinstance(entry, (str, int)):
                        raise ImproperlyConfigured(
                            'Item "{0}" of parameter "{1}" in {2} has wrong type.'
                            .format(entry, param_name, cls.type_name))

        if missing_parameters:
            raise ImproperlyConfigured(
                'Missing parameter(s) {0} for "{1}". '
                'See Sphinx documentation for {1} configuration.'
                .format(missing_parameters, cls.type_name))


class IndexConfiguration(Configuration):
    """
    Responsible for configuring a Sphinx source and index
    """
    type_name = 'index'
    valid_parameters = constants.index_parameters
    mandatory_parameters = constants.index_mandatory_parameters
    multi_valued_parameters = constants.index_multi_valued_parameters


class SourceConfiguration(Configuration):
    """
    Responsible for configuring a Sphinx source and index
    """
    type_name = 'source'
    valid_parameters = constants.source_parameters
    mandatory_parameters = constants.source_mandatory_parameters
    multi_valued_parameters = constants.source_multi_valued_parameters


class IndexerConfiguration(Configuration):
    """
    Responsible for configuring a Sphinx source and index
    """
    type_name = 'indexer'
    valid_parameters = constants.indexer_parameters

    def __init__(self, params):
        super(IndexerConfiguration, self).__init__('', params)


class SearchdConfiguration(Configuration):
    """
    Responsible for configuring a Sphinx source and index
    """
    type_name = 'searchd'
    valid_parameters = constants.searchd_parameters
    mandatory_parameters = constants.searchd_mandatory_parameters

    def __init__(self, params):
        super(SearchdConfiguration, self).__init__('', params)
