from custodian.command import Command, COMMAND_METHOD
from custodian.exceptions import CommandExecutionFailureException
from custodian.objects.model import Object
from custodian.records.model import Record
from custodian.records.query import Query


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

    def create(self, record: Record):
        """
        Creates a new record in the Custodian
        :param record:
        :return:
        """
        data = self.client.execute(
            command=Command(name=self._get_record_command_name(record.obj), method=COMMAND_METHOD.POST),
            data=record.serialize()
        )
        return Record(obj=record.obj, **data)

    def update(self, record: Record):
        """
        Updates an existing record in the Custodian
        """
        data = self.client.execute(
            command=Command(name=self._get_record_command_name(record.obj, record.get_pk()), method=COMMAND_METHOD.PUT),
            data=record.serialize()
        )
        record.__init__(obj=record.obj, **data)
        return record

    def delete(self, record: Record):
        """
        Deletes the record from the Custodian
        :param record:
        :return:
                """
        self.client.execute(
            command=Command(
                name=self._get_record_command_name(record.obj, record.get_pk()),
                method=COMMAND_METHOD.DELETE
            )
        )
        setattr(record, record.obj.key, None)

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

    def query(self, obj: Object):
        return Query(obj)
