class BaseField:
    type = None

    def __init__(self, name: str, optional: bool = False, default=None):
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
