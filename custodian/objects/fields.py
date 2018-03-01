from typing import NamedTuple

from custodian.exceptions import FieldDoesNotExistException, ImproperlyConfiguredFieldException


class BaseField:
    type = None

    def __init__(self, name: str, optional: bool = False, default=None, **kwargs):
        if self.type is None:
            raise NotImplementedError('Attempted to instantiate abstract field class')
        self.name = name
        self.optional = optional
        self.default = default

    def serialize(self) -> dict:
        return {
            'name': self.name,
            'type': self.type,
            'optional': self.optional,
            'default': self.default
        }

    cast_func = None

    def from_raw(self, value):
        if self.cast_func is None:
            raise NotImplementedError
        else:
            return self.cast_func(value)

    def to_raw(self, value):
        if self.cast_func is None:
            raise NotImplementedError
        else:
            if value is None:
                if self.optional:
                    return None
                else:
                    raise ValueError('"{}" field is required'.format(self.name))
            return self.cast_func(value)

    @classmethod
    def get_default_value(cls):
        return cls.cast_func()


class NumberField(BaseField):
    type: str = 'number'
    cast_func = float


class IntegerField(BaseField):
    type: str = 'number'
    cast_func = int


class StringField(BaseField):
    type: str = 'string'
    cast_func = str


class BooleanField(BaseField):
    type: str = 'bool'
    cast_func = bool


class ArrayField(BaseField):
    type: str = 'array'
    cast_func = lambda x: x


class ObjectField(BaseField):
    type: str = 'object'
    cast_func = lambda x: x


class RelatedObjectField(BaseField):
    LINK_TYPES = NamedTuple('LINK_TYPE', [('INNER', str), ('OUTER', str)])(INNER='inner', OUTER='outer')

    type: str = 'relatedObject'
    _many: bool = False

    def __init__(self, name: str, obj, link_type: str, optional: bool = False, outer_link_field: str = None,
                 many=False, **kwargs):
        if link_type == self.LINK_TYPES.OUTER and outer_link_field is None:
            raise ImproperlyConfiguredFieldException('"outer_link_field" must be specified for "outer" link type')

        self._link_type = link_type
        self._obj = obj
        self._many = many
        self._outer_link_field = outer_link_field
        super(RelatedObjectField, self).__init__(name, optional, default=None)

    def serialize(self):
        return {
            **{
                'name': self.name,
                'type': 'object' if not self._many else 'array',
                'optional': self.optional,
                'linkMeta': self._obj.name,
                'linkType': self._link_type,

            },
            **({'outerLinkField': self._outer_link_field} if self._outer_link_field else {})
        }

    def to_raw(self, value):
        if self._link_type == self.LINK_TYPES.OUTER:
            return None
        else:
            return value

    def from_raw(self, value):
        return value

    @property
    def obj(self):
        return self._obj

    @property
    def link_type(self):
        return self._link_type


class FieldsManager:
    fields = {
        NumberField.type: NumberField,
        StringField.type: StringField,
        BooleanField.type: BooleanField,
        ArrayField.type: ArrayField,
        ObjectField.type: ObjectField,
        RelatedObjectField.type: RelatedObjectField
    }

    @classmethod
    def get_field_by_type(cls, field_type: str):
        """
        Returns field associated with the given type
        :param field_type:
        :return:
        """
        try:
            return cls.fields[field_type]
        except IndexError:
            raise FieldDoesNotExistException()
