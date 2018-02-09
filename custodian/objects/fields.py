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


class NumberField(BaseField):
    type: str = 'number'


class StringField(BaseField):
    type: str = 'string'


class BooleanField(BaseField):
    type: str = 'bool'


class ArrayField(BaseField):
    type: str = 'array'


class ObjectField(BaseField):
    type: str = 'bool'


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
