from .configuration import indexes_configurator
from .exceptions import ImproperlyConfigured
from .fields import Field
from .manager import Manager


class MetaIndex(type):
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
        new_class = super(MetaIndex, mcs).__new__(mcs, name, bases, attrs)
        meta = new_class.Meta

        # create a dictionary of *model* fields.
        model_fields = {}
        for model_field in model_meta.local_fields:
            model_fields[model_field.name] = model_field

        ### populate Meta with fields
        meta.fields = []
        for field_name in attrs:
            # ignore non-fields
            if not isinstance(attrs[field_name], Field):
                continue
            field = attrs[field_name]

            # set field name and add it to meta
            field._value = field_name
            meta.fields.append(field)

            # set a creation_counter and a model_field_name
            # to later use
            if field.model_attr in model_fields:
                field.creation_counter = model_fields[field.model_attr].creation_counter
            else:
                raise ImproperlyConfigured(
                    '"{model_field}" model field in "{index_name}.{field_name}"'
                    ' not found. Available model fields: {model_fields}'
                    .format(model_field=field.model_attr,
                            field_name=field.name,
                            index_name=name,
                            model_fields=list(model_fields.keys())))

        # order fields by creation_counter so they have same order
        # of Django fields. This is required to ensure
        # the query produced by Meta.query is consistent.
        meta.fields.sort(key=lambda x: x.creation_counter)

        # register the field in our index configurator
        # so it is indexed by Sphinx.
        indexes_configurator.register(new_class)

        # default manager
        if not hasattr(new_class, 'objects'):
            new_class.objects = Manager(new_class)

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
