from custodian.exceptions import FieldDoesNotExistException


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

    @classmethod
    def from_raw(cls, value):
        if cls.cast_func is None:
            raise NotImplementedError
        else:
            return cls.cast_func(value)

    @classmethod
    def to_raw(cls, value):
        if cls.cast_func is None:
            raise NotImplementedError
        else:
            return cls.cast_func(value)

    @classmethod
    def get_default_value(cls):
        return cls.cast_func()


class NumberField(BaseField):
    type: str = 'number'
    cast_func = float


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
    type: str = 'bool'
    cast_func = lambda x: x


class FieldsManager:
    fields = {
        NumberField.type: NumberField,
        StringField.type: StringField,
        BooleanField.type: BooleanField,
        ArrayField.type: ArrayField,
        ObjectField.type: ObjectField
    }

    @classmethod
    def get_field_by_type(cls, field_type: str):
        """
        Returns field associated with given type
        :param field_type:
        :return:
        """
        try:
            return cls.fields[field_type]
        except IndexError:
            raise FieldDoesNotExistException()
