from collections import OrderedDict
from .configuration import indexes_configurator
from .exceptions import ImproperlyConfigured
from .fields import Field
from .query import SearchQuerySet
from .manager import IndexManager


class MetaIndex(type):

    # Ensures the fields are ordered when first created.
    @classmethod
    def __prepare__(mcs, name, bases):
        return OrderedDict()

    def __new__(mcs, name, bases, attrs):
        # exclude ``Index`` itself
        parents = [b for b in bases if isinstance(b, MetaIndex)]
        if not parents:
            return super(MetaIndex, mcs).__new__(mcs, name, bases, attrs)

        meta = attrs['Meta']

        model_meta = getattr(meta.model, '_meta', None)
        if not model_meta:
            raise ImproperlyConfigured('{index_name}.Meta.model "{model}" '
                                       'is not a Django model'.format(index_name=name,
                                                                      model=meta.model))

        # create new class
        new_class = super(MetaIndex, mcs).__new__(mcs, name, bases, dict(attrs))
        meta = new_class.Meta

        # populate Meta with fields
        meta.fields = []
        for field_name in attrs:
            # ignore non-fields
            if not isinstance(attrs[field_name], Field):
                continue
            field = attrs[field_name]

            # set field name and add it to meta
            field._value = field_name
            meta.fields.append(field)

        # register the field in our index configurator
        # so it is indexed by Sphinx.
        indexes_configurator.register(new_class)

        # managers
        has_any_manager = False
        for manager_name in attrs:
            # ignore non-managers
            if not isinstance(attrs[manager_name], IndexManager):
                continue

            # construct the manager from the queryset, init it with this index and
            # set it to the index
            manager = attrs[manager_name].from_queryset(SearchQuerySet)(new_class)
            setattr(new_class, manager_name, manager)
            has_any_manager = True

        if not has_any_manager:
            new_class.objects = IndexManager.from_queryset(SearchQuerySet)(new_class)

        return new_class


class Index(metaclass=MetaIndex):
    """
    Base class of all indexes.
    """

    class Meta:
        model = None

    @classmethod
    def build_name(cls):
        """
        Returns a string representing the index
        on the sphinx.conf.
        """
        meta = getattr(cls.Meta.model, '_meta', None)
        assert meta is not None
        return "%s_%s" % (meta.app_label, cls.__name__.lower())

    @classmethod
    def get_model_field(cls, model_attr):
        field, _, _, _ = cls.Meta.model._meta.get_field_by_name(model_attr)
        return field.get_attname_column()[1]
