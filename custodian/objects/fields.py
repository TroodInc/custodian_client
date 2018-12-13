import datetime
from typing import NamedTuple, List

import dateparser

from custodian.exceptions import FieldDoesNotExistException, ImproperlyConfiguredFieldException

LINK_TYPES = NamedTuple('LINK_TYPE', [('INNER', str), ('OUTER', str)])(INNER='inner', OUTER='outer')


class BaseField:
    type = None
    parent_obj = None

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

    def set_parent_obj(self, parent_obj):
        setattr(self, 'parent_obj', parent_obj)

    def from_raw(self, value):
        if self.cast_func is None:
            raise NotImplementedError
        else:
            if value is not None:
                return self.cast_func(value)
            else:
                return None

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


class DateTimeField(BaseField):
    type: str = 'datetime'
    cast_func = datetime.datetime

    def from_raw(self, value):
        if value and isinstance(value, str):
            return dateparser.parse(value)
        return value

    def to_raw(self, value: datetime.datetime):
        return value.isoformat() if value else None


class TimeField(BaseField):
    type: str = 'time'
    cast_func = datetime.time

    def from_raw(self, value):
        if value and isinstance(value, str):
            return dateparser.parse(value)
        return value

    def to_raw(self, value: datetime.time):
        return value.isoformat() if value else None


class DateField(BaseField):
    type: str = 'date'
    cast_func = datetime.date

    def from_raw(self, value):
        if value and isinstance(value, str):
            return dateparser.parse(value).date()
        return value

    def to_raw(self, value: datetime.date):
        return value.isoformat() if value else None


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
    type: str = 'relatedObject'
    many: bool = False
    _reverse_field = None

    def __init__(self, name: str, obj, link_type: str, optional: bool = False, outer_link_field: str = None,
                 many=False, reverse_field=None, **kwargs):
        if link_type == LINK_TYPES.OUTER and outer_link_field is None:
            raise ImproperlyConfiguredFieldException('"outer_link_field" must be specified for "outer" link type')

        self.link_type = link_type
        self.obj = obj
        self.many = many
        self.outer_link_field = outer_link_field
        self._reverse_field = reverse_field
        super(RelatedObjectField, self).__init__(name, optional, default=None)

    def serialize(self):
        return {
            **{
                'name': self.name,
                'type': 'object' if not self.many else 'array',
                'optional': self.optional,
                'linkMeta': self.obj.name,
                'linkType': self.link_type,

            },
            **({'outerLinkField': self.outer_link_field} if self.outer_link_field else {})
        }

    def to_raw(self, value):
        if value is None:
            if self.optional:
                return None
            else:
                raise ValueError('"{}" field is required'.format(self.name))
        return self.obj.fields[self.obj.key].cast_func(value)

    def from_raw(self, value):
        # Try to cast potential ids from string to int
        if isinstance(value, str):
            try:
                value = int(value)
                return value
            except ValueError:
                return value
        return value

    def get_pk(self):
        # @todo: must return pk name based on schema
        return 'id'

    @property
    def reverse_field(self):
        if not self._reverse_field:
            if self.link_type == LINK_TYPES.INNER:
                for field in self.obj.fields.values():
                    if isinstance(field, RelatedObjectField):
                        if field.outer_link_field == self.name and field.obj.name == self.parent_obj.name:
                            self._reverse_field = field
            else:
                self._reverse_field = self.obj.fields.get(self.outer_link_field)
        return self._reverse_field


class GenericField(BaseField):
    type: str = 'generic'
    cast_func = lambda x, y: y
    _reverse_field = None

    def __init__(self, name: str, link_type: str, obj=None, objs: List[object] = None, optional: bool = False,
                 outer_link_field: str = None, reverse_field=None, **kwargs):
        if link_type == LINK_TYPES.OUTER and outer_link_field is None:
            raise ImproperlyConfiguredFieldException('"outer_link_field" must be specified for "outer" link type')

        if link_type == LINK_TYPES.INNER and objs is None:
            raise ImproperlyConfiguredFieldException('"obj" must be specified for "inner" link type')

        self.link_type = link_type
        self.obj = obj
        self.objs = objs
        self.outer_link_field = outer_link_field
        self._reverse_field = reverse_field
        super(GenericField, self).__init__(name, optional, default=None)

    def serialize(self):
        return {
            **{
                'name': self.name,
                'type': self.type,
                'optional': self.optional,
                'linkType': self.link_type,

            },
            **({'outerLinkField': self.outer_link_field} if self.outer_link_field else {}),
            **({'linkMeta': self.obj.name} if self.link_type == LINK_TYPES.OUTER else {}),
            **({'linkMetaList': [obj.name for obj in self.objs]} if self.link_type == LINK_TYPES.INNER else {})
        }

    def to_raw(self, value: dict):
        if value is None:
            return None
        if self.link_type == LINK_TYPES.OUTER:
            return self.obj.fields[self.obj.key].to_raw(value)
        else:
            assert type(value) is dict
            assert '_object' in value.keys(), "Generic field value should contain '_object' key"
            assert isinstance(value['_object'], str)
            return value

    def from_raw(self, value):
        return value


class ObjectsField(BaseField):
    type: str = 'objects'
    cast_func = lambda x, y: y
    _reverse_field = None

    def __init__(self, name: str, link_type: str, obj=None, optional: bool = False,
                 outer_link_field: str = None, reverse_field=None, **kwargs):
        if link_type == LINK_TYPES.OUTER and outer_link_field is None:
            raise ImproperlyConfiguredFieldException('"outer_link_field" must be specified for "outer" link type')

        self.link_type = link_type
        self.obj = obj
        self.outer_link_field = outer_link_field
        self._reverse_field = reverse_field
        super(ObjectsField, self).__init__(name, optional, default=None)

    def serialize(self):
        return {
            'name': self.name,
            'type': self.type,
            'optional': self.optional,
            'linkMeta': self.obj.name,
            'linkType': self.link_type,

        }

    def to_raw(self, value):
        values = []
        for value_item in value:
            values.append(self.obj.fields[self.obj.key].cast_func(value_item))
        return values

    def from_raw(self, value):
        # Try to cast potential ids from string to int
        if isinstance(value, str):
            try:
                value = int(value)
                return value
            except ValueError:
                return value
        return value


class FieldsManager:
    fields = {
        NumberField.type: NumberField,
        StringField.type: StringField,
        BooleanField.type: BooleanField,
        ArrayField.type: ArrayField,
        ObjectField.type: ObjectField,
        RelatedObjectField.type: RelatedObjectField,
        DateTimeField.type: DateTimeField,
        DateField.type: DateField,
        GenericField.type: GenericField,
        ObjectsField.type: ObjectsField
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
