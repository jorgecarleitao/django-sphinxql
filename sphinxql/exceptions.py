
class SphinxError(Exception):
    """
    general exception of Sphinx so users can catch any Sphinx error.
    """
    pass


class ImproperlyConfigured(SphinxError):
    """somehow improperly configured"""
    pass


class NotSupportedError(SphinxError):
    """Something not support by Sphinx"""
    pass
