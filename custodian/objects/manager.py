from custodian.command import Command, COMMAND_METHOD
from custodian.objects.model import Object


class ObjectsManager:
    _command_name = 'meta'

    def __init__(self, client):
        self.client = client

    def create(self, obj) -> Object:
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

    def update(self):
        pass

    def delete(self):
        pass
