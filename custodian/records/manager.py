from custodian.command import Command, COMMAND_METHOD
from custodian.exceptions import CommandExecutionFailureException
from custodian.objects.model import Object
from custodian.records.model import Record


class RecordsManager:
    _base_command_name = 'data/single'

    def __init__(self, client):
        self.client = client

    def _get_record_command_name(self, obj: Object, record_id=None) -> str:
        """
        Constructs an uri chunk for API communication
        :param obj:
        :param record_id:
        :return:
        """
        args = [self._base_command_name, obj.name]
        if record_id:
            args.append(str(record_id))
        return '/'.join(args)

    def create(self, record):
        """
        Creates a new record in the Custodian
        :param record:
        :return:
        """
        data = self.client.execute(
            command=Command(name=self._get_record_command_name(record.obj), method=COMMAND_METHOD.POST)
        )
        return Record(obj=record.obj, **data)

    def update(self):
        pass

    def delete(self):
        pass

    def get(self, obj: Object, record_id: str):
        """
        Retrieves an existing record from Custodian
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
