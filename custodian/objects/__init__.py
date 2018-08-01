from collections import OrderedDict
from typing import List

from custodian.objects.actions import Action
from custodian.objects.fields import BaseField, FieldsManager


class Object:
    name = None
    cas = None
    _key = None
    _fields = None
    _actions = None
    _evaluated = None
    _objects_manager = None

    def __init__(self, name: str, cas: bool, objects_manager, key: str = None, fields: List[BaseField] = None,
                 actions: List[Action] = None):
        self.name = name
        self.cas = cas
        self._key = key
        self._fields = OrderedDict([(x.name, x) for x in fields]) if fields else None
        self._evaluated = bool(fields) and bool(key)
        self._objects_manager = objects_manager
        if self._fields:
            for field in self._fields.values():
                field.set_parent_obj(self)
        self._actions = actions

    @property
    def key(self):
        if not self._evaluated:
            self._evaluate()
        return self._key

    @property
    def fields(self):
        if not self._evaluated:
            self._evaluate()
        return self._fields

    @property
    def actions(self):
        if not self._evaluated:
            self._evaluate()
        return self._actions

    def _evaluate(self):
        obj = self._objects_manager.get(self.name)
        self._fields = obj.fields
        self._key = obj.key
        self._evaluated = True

    def serialize(self):
        return {
            'name': self.name,
            'key': self.key,
            'cas': self.cas,
            'fields': [x.serialize() for x in self.fields.values()],
            'actions': [x.serialize() for x in self._actions] if self._actions else []
        }

    def __repr__(self):
        return '<Custodian object "{}">'.format(self.name)


class METHODS:
    RETRIEVE = 'retrieve'
    CREATE = 'create'
    REMOVE = 'remove'
    UPDATE = 'update'
