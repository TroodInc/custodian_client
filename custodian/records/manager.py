from custodian.command import Command, COMMAND_METHOD
from custodian.exceptions import CommandExecutionFailureException
from custodian.objects.manager import ObjectsManager
from custodian.objects.model import Object
from custodian.records.model import Record


class RecordsManager:

    def __init__(self, client):
        self.client = client

    def _get_record_command_name(self, obj: Object, record_id) -> str:
        return '/'.join([ObjectsManager.get_object_command_name(obj.name), str(record_id)])

    def create(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

    def get(self, obj: Object, record_id: str):
        """
        Retrieves existing record from Custodian
        :param obj:
        :param record_id:
        :return:
        """
        try:
            data = self.client.execute(
                command=Command(name=self._get_record_command_name(obj, record_id), method=COMMAND_METHOD.GET)
            )
            return Record(obj=obj, **data)
        except CommandExecutionFailureException:
            return None
