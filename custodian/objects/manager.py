from custodian.command import Command, COMMAND_METHOD
from custodian.exceptions import CommandExecutionFailureException, ObjectUpdateException, ObjectCreateException
from custodian.objects import Object
from custodian.objects.serializer import ObjectSerializer


class ObjectsManager:
    _base_command_name = 'meta'

    _cache = None

    def __init__(self, client):
        self.client = client
        self._cache = {}

    @classmethod
    def get_object_command_name(cls, object_name: str):
        """
        Constructs API command for existing Custodian object
        :param obj:
        :return:
        """
        return '/'.join([cls._base_command_name, object_name])

    def create(self, obj: Object) -> Object:
        """
        Creates new object in Custodian
        :param obj:
        :return:
        """
        data, ok = self.client.execute(
            command=Command(name=self._base_command_name, method=COMMAND_METHOD.PUT),
            data=obj.serialize()
        )
        if ok:
            return obj
        else:
            raise ObjectCreateException(data.get('msg'))

    def update(self, obj: Object) -> Object:
        """
        Updates existing object in Custodian
        :param obj:
        :return:
        """
        data, ok = self.client.execute(
            command=Command(name=self.get_object_command_name(obj.name), method=COMMAND_METHOD.POST),
            data=obj.serialize()
        )
        if ok:
            self._cache[obj.name] = obj
            return obj
        else:
            raise ObjectUpdateException(data.get('msg'))

    def delete(self, obj: Object) -> Object:
        """
        Deletes existing object from Custodian
        :param obj:
        :return:
        """

        self.client.execute(
            command=Command(name=self.get_object_command_name(obj.name), method=COMMAND_METHOD.DELETE)
        )
        if obj.name in self._cache:
            del self._cache[obj.name]
        return obj

    def get(self, object_name):
        """
        Retrieves existing object from Custodian by name
        :param object_name:
        """
        if not object_name in self._cache:
            data, ok = self.client.execute(
                command=Command(name=self.get_object_command_name(object_name), method=COMMAND_METHOD.GET)
            )
            obj = ObjectSerializer.deserialize(data, self) if ok else None
            if obj:
                self._cache[object_name] = obj
        return self._cache.get(object_name)

    def get_all(self):
        """
        Retrieves a list of existing objects from Custodian
        :return:
        """
        data, ok = self.client.execute(
            command=Command(name=self.get_object_command_name(''), method=COMMAND_METHOD.GET)
        )
        if ok and data:
            return [ObjectSerializer.deserialize(object_data, self) for object_data in data]
        else:
            return []
