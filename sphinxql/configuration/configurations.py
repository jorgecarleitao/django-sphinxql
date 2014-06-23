from . import constants
from ..exceptions import ImproperlyConfigured


class Configuration(object):
    """
    A generic Sphinx configuration.

    Has a type, a type_name and parameters in a dictionary
    form.
    """
    type_name = None
    valid_parameters = tuple()

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
            if not isinstance(param_values, list):
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
        Formats this configuration into a string
        ready for sphinx.conf.
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
        Checks that all parameters `params` are valid
        for this configuration.
        """
        for param in params:
            if param not in cls.valid_parameters:
                raise ImproperlyConfigured(
                    'Invalid parameter "{0}" for "{1}". '
                    'See Sphinx documentation of "{1} configuration".'
                    .format(param, cls.type_name))


class IndexConfiguration(Configuration):
    """
    Responsible for configuring a Sphinx source and index
    """
    type_name = 'index'
    valid_parameters = constants.index_parameters


class SourceConfiguration(Configuration):
    """
    Responsible for configuring a Sphinx source and index
    """
    type_name = 'source'
    valid_parameters = constants.source_parameters


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

    def __init__(self, params):
        super(SearchdConfiguration, self).__init__('', params)
