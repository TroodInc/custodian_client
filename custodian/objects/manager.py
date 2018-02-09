from custodian.command import Command, COMMAND_METHOD
from custodian.objects.model import Object


class ObjectsManager:
    _command_name = 'meta'

    def __init__(self, client):
        self.client = client

    def _get_object_command_name(self, object_name: str):
        """
        Constructs API command for existing Custodian object
        :param obj:
        :return:
        """
        return '/'.join([self._command_name, object_name])

    def create(self, obj: Object) -> Object:
        """
        Creates new object in Custodian
        :param obj:
        :return:
        """
        self.client.execute(
            command=Command(name=self._command_name, method=COMMAND_METHOD.POST),
            data=obj.serialize()
        )
        return obj

    def update(self, obj: Object) -> Object:
        """
        Updates existing object in Custodian
        :param obj:
        :return:
        """
        self.client.execute(
            command=Command(name=self._get_object_command_name(obj.name), method=COMMAND_METHOD.PUT),
            data=obj.serialize()
        )
        return obj

    def delete(self, obj: Object) -> Object:
        """
        Deletes existing object from Custodian
        :param obj:
        :return:
        """

        self.client.execute(
            command=Command(name=self._get_object_command_name(obj.name), method=COMMAND_METHOD.DELETE)
        )
        return obj

    def get(self, object_name):
        """
        Retrieves existing object from Custodian by name
        :param object_name:
        """
        data = self.client.execute(
            command=Command(name=self._get_object_command_name(object_name), method=COMMAND_METHOD.GET)
        )
        return Object.deserialize(data)

    def get_all(self):
        """
        Retrieves a list of existing objects from Custodian
        :return:
        """
        # TODO: Implement this method
        raise NotImplementedError
