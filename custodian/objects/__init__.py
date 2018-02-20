from collections import OrderedDict
from typing import List

from custodian.objects.fields import BaseField, FieldsManager


class Object:
    name = None
    key = None
    cas = None
    fields = None

    def __init__(self, name: str, key: str, cas: bool, fields: List[BaseField]):
        self.name = name
        self.key = key
        self.cas = cas
        self.fields = OrderedDict([(x.name, x) for x in fields])

    def serialize(self):
        return {
            'name': self.name,
            'key': self.key,
            'cas': self.cas,
            'fields': [x.serialize() for x in self.fields.values()]
        }

    @classmethod
    def deserialize(cls, data):
        data['fields'] = [FieldsManager.get_field_by_type(x['type'])(**x) for x in data['fields']]
        return Object(**data)
