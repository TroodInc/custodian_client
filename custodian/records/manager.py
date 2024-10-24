from custodian.command import Command, COMMAND_METHOD
from custodian.exceptions import CommandExecutionFailureException, RecordAlreadyExistsException, ObjectUpdateException, \
    RecordUpdateException, CasFailureException, ObjectDeletionException
from custodian.objects import Object
from custodian.records.model import Record
from custodian.records.query import Query


class RecordsManager:
    _base_single_command_name = 'data/single'
    _base_bulk_command_name = 'data/bulk'

    def __init__(self, client):
        self.client = client

    def _get_single_record_command_name(self, obj: Object, record_id=None) -> str:
        """
        Constructs an uri chunk for API communication
        :param obj:
        :param record_id:
        :return:
        """
        args = [self._base_single_command_name, obj.name]
        if record_id:
            args.append(str(record_id))
        return '/'.join(args)

    def _get_bulk_command_name(self, obj: Object) -> str:
        """
        Constructs an uri chunk for API communication
        :param obj:
        :return:
        """
        args = [self._base_bulk_command_name, obj.name]
        return '/'.join(args)

    def create(self, record: Record, **kwargs) -> Record:
        """
        Creates a new record in the Custodian
        :param record:
        :return:
        """
        data, ok = self.client.execute(
            command=Command(name=self._get_single_record_command_name(record.obj), method=COMMAND_METHOD.PUT),
            data=record.serialize(),
            params=kwargs
        )
        if ok:
            return Record(obj=record.obj, **data)
        elif data.get('msg', '').find('duplicate') != -1:
            raise RecordAlreadyExistsException
        else:
            raise CommandExecutionFailureException(data.get('msg'))

    def update(self, record: Record, **kwargs):
        """
        Updates an existing record in the Custodian
        """
        data, ok = self.client.execute(
            command=Command(name=self._get_single_record_command_name(record.obj, record.get_pk()),
                            method=COMMAND_METHOD.POST),
            data=record.serialize(),
            params=kwargs
        )
        if ok:
            record.__init__(obj=record.obj, **data)
            return record
        else:
            if data.get('code') == 'cas_failed':
                raise CasFailureException(data.get('msg', ''))
            else:
                raise RecordUpdateException(data.get('msg', ''))

    def delete(self, record: Record):
        """
        Deletes the record from the Custodian
        :param record:
        :return:
                """
        self.client.execute(
            command=Command(
                name=self._get_single_record_command_name(record.obj, record.get_pk()),
                method=COMMAND_METHOD.DELETE
            )
        )
        setattr(record, record.obj.key, None)

    def get(self, obj: Object, record_id: str, **kwargs):
        """
        Retrieves an existing record from Custodian
        :param obj:
        :param record_id:
        :return:
        """
        data, ok = self.client.execute(
            command=Command(name=self._get_single_record_command_name(obj, record_id), method=COMMAND_METHOD.GET),
            params=kwargs
        )
        return Record(obj=obj, **data) if ok else None

    def _query(self, obj: Object, query_string: str, **kwargs):
        """
        Performs an Custodian API call and returns a list of records
        :param obj:
        :param query_string:
        :return:
        """
        data, _ = self.client.execute(
            command=Command(name=self._get_bulk_command_name(obj), method=COMMAND_METHOD.GET),
            params={'q': query_string, **kwargs}
        )

        records = []
        for record_data in data:
            records.append(Record(obj=obj, **record_data))
        return records

    def query(self, obj: Object, depth=1) -> Query:
        """
        Returns a Query object
        :param obj:
        :return:
        """
        return Query(obj, self, depth=depth)

    def _check_records_have_same_object(self, *records: Record):
        """
        Bulk operations are permitted only for one object at time
        :param records:
        :return:
        """
        obj = records[0].obj
        for record in records[1:]:
            assert obj.name == record.obj.name, 'Attempted to perform bulk operation on the list of diverse records'
        return True

    def bulk_create(self, *records: Record):
        """
        Creates new records in the Custodian
        :param records:
        :return:
        """
        self._check_records_have_same_object(*records)
        obj = records[0].obj
        data, ok = self.client.execute(
            command=Command(name=self._get_bulk_command_name(obj), method=COMMAND_METHOD.PUT),
            data=[record.serialize() for record in records]
        )
        if ok:
            for i in range(0, len(data)):
                records[i].__init__(obj, **data[i])
            return list(records)
        else:
            raise CommandExecutionFailureException(data.get('msg'))

    def bulk_update(self, *records: Record):
        """
        :return:
        """
        self._check_records_have_same_object(*records)
        obj = records[0].obj
        data, ok = self.client.execute(
            command=Command(name=self._get_bulk_command_name(obj), method=COMMAND_METHOD.POST),
            data=[record.serialize() for record in records]
        )
        if ok:
            for i in range(0, len(data)):
                records[i].__init__(obj, **data[i])
            return list(records)
        else:
            raise ObjectUpdateException(data.get('msg'))

    def bulk_delete(self, *records: Record):
        """
        Deletes records from the Custodian
        :return:
        """
        if records:
            self._check_records_have_same_object(*records)
            obj = records[0].obj
            data, ok = self.client.execute(
                command=Command(name=self._get_bulk_command_name(obj), method=COMMAND_METHOD.DELETE),
                data=[{obj.key: record.get_pk()} for record in records]
            )
            if ok:
                for record in records:
                    record.id = None
                return list(records)
            else:
                raise ObjectDeletionException(data.get('msg'))
        else:
            return []
