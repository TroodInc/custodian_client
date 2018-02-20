import pytest
import requests_mock
from hamcrest import *

from custodian.client import Client
from custodian.exceptions import CommandExecutionFailureException, RecordAlreadyExistsException
from custodian.objects import Object
from custodian.records.model import Record


def test_client_retrieves_existing_record(person_record: Record, client: Client):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            '/'.join([client.server_url, 'data/single/{}/{}'.format(person_record.obj.name, person_record.get_pk())]),
            json={
                'status': 'OK',
                'data': person_record.serialize()
            }
        )
        record = client.records.get(person_record.obj, person_record.get_pk())
        assert_that(record, is_(instance_of(Record)))


def test_client_returns_none_for_nonexistent_record(person_record: Record, client: Client):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            '/'.join([client.server_url, 'data/single/{}/{}'.format(person_record.obj.name, person_record.get_pk())]),
            json={
                'status': 'FAIL',
                'data': {}
            }
        )
        record = client.records.get(person_record.obj, person_record.get_pk())
        assert_that(record, is_(None))


def test_client_returns_new_record_on_record_creation(person_record: Record, client: Client):
    person_record.id = None
    assert_that(person_record.exists(), is_not(True))
    record_data = person_record.serialize()
    record_data['id'] = 45
    with requests_mock.Mocker() as mocker:
        mocker.put(
            '/'.join([client.server_url, 'data/single/{}'.format(person_record.obj.name)]),
            json={
                'status': 'OK',
                'data': record_data
            }
        )
        record = client.records.create(person_record)
        assert_that(record, is_(instance_of(Record)))
        assert_that(record.exists())
        assert_that(record.id, equal_to(45))


def test_client_deletes(person_record: Record, client: Client):
    assert_that(person_record.exists())
    record_data = person_record.serialize()
    with requests_mock.Mocker() as mocker:
        mocker.delete(
            '/'.join([client.server_url, 'data/single/{}/{}'.format(person_record.obj.name, person_record.get_pk())]),
            json={
                'status': 'OK',
                'data': record_data
            }
        )
        client.records.delete(person_record)
        assert_that(person_record.exists(), is_not(True))


def test_client_returns_updated_record_on_record_update(person_record: Record, client: Client):
    record_data = person_record.serialize()
    record_data['is_active'] = False
    with requests_mock.Mocker() as mocker:
        mocker.post(
            '/'.join([client.server_url, 'data/single/{}/{}'.format(person_record.obj.name, person_record.get_pk())]),
            json={
                'status': 'OK',
                'data': record_data
            }
        )
        record = client.records.update(person_record)
        assert_that(record, is_(instance_of(Record)))
        assert_that(record.exists())
        assert_that(record.is_active, is_(False))


def test_client_returns_iterable_of_records_on_bulk_query(person_object: Object, person_record: Record, client: Client):
    query = client.records.query(person_object).filter(address__city_id__eq=45)
    with requests_mock.Mocker() as mocker:
        mocker.get(
            '/'.join([client.server_url, 'data/bulk/{}'.format(person_object.name)]),
            json={
                'status': 'OK',
                'data': [
                    # nothing terrible in is that records are duplicated
                    person_record.serialize(),
                    person_record.serialize()
                ]
            }
        )
        assert_that(len(query), equal_to(2))
        for record in query:
            assert_that(record, instance_of(Record))


def test_client_returns_list_of_records_on_bulk_create(person_object: Object, client: Client):
    records_to_create = [
        Record(
            obj=person_object,
            name='Ivan Petrov',
            is_active=False
        ),
        Record(
            obj=person_object,
            name='Nikolay Kozlov',
            is_active=True
        )
    ]

    with requests_mock.Mocker() as mocker:
        mocker.post(
            '/'.join([client.server_url, 'data/bulk/{}'.format(person_object.name)]),
            json={
                'status': 'OK',
                'data': [
                    {**x.serialize(), **{'id': records_to_create.index(x) + 1}} for x in records_to_create
                ]
            }
        )
        created_records = client.records.bulk_create(*records_to_create)
        for created_record in created_records:
            assert_that(created_record, instance_of(Record))
            assert_that(created_record.name)
        assert_that(created_records, equal_to(records_to_create))


def test_client_returns_list_of_records_on_bulk_update(person_object: Object, client: Client):
    records_to_update = [
        Record(
            obj=person_object,
            name='Ivan Petrov',
            is_active=False,
            id=23
        ),
        Record(
            obj=person_object,
            name='Nikolay Kozlov',
            is_active=True,
            id=34
        )
    ]

    with requests_mock.Mocker() as mocker:
        mocker.put(
            '/'.join([client.server_url, 'data/bulk/{}'.format(person_object.name)]),
            json={
                'status': 'OK',
                'data': [x.serialize() for x in records_to_update]
            }
        )
        updated_records = client.records.bulk_update(*records_to_update)
        for updated_record in updated_records:
            assert_that(updated_record, instance_of(Record))
            assert_that(updated_record.name)
        assert_that(updated_records, equal_to(records_to_update))


def test_client_returns_list_of_records_without_pk_value_on_bulk_delete(person_object: Object, client: Client):
    records_to_delete = [
        Record(
            obj=person_object,
            name='Ivan Petrov',
            is_active=False,
            id=23
        ),
        Record(
            obj=person_object,
            name='Nikolay Kozlov',
            is_active=True,
            id=34
        )
    ]

    with requests_mock.Mocker() as mocker:
        mocker.delete(
            '/'.join([client.server_url, 'data/bulk/{}'.format(person_object.name)]),
            json={
                'status': 'OK'
            }
        )
        client.records.bulk_delete(*records_to_delete)
        for record in records_to_delete:
            assert_that(not record.exists())


class TestCustodianIntegrationSeries:
    def test_the_database_contains_person_object(self, client: Client, person_object: Object):
        """
        Remove any existing objects and create a new "Person" object
        :param client:
        """
        for obj in client.objects.get_all():
            client.objects.delete(obj)
        client.objects.create(person_object)
        assert_that(client.objects.get_all(), has_length(1))

    def test_new_record_is_created(self, person_record: Record, client: Client):
        """
        Create a new record and check it has PK field assigned
        :param person_record:
        :param client:
        """
        person_record.id = None
        assert_that(person_record.id, is_(None))
        # create new record
        person_record = client.records.create(person_record)
        assert_that(person_record.id, instance_of(int))

    def test_new_record_can_be_retrieved_by_pk(self, person_record: Record, client: Client):
        """
        Create a new record and check it has PK field assigned
        :param person_record:
        :param client:
        """
        person_record.id = None
        person_record = client.records.create(person_record)
        assert_that(client.records.get(person_record.obj, person_record.get_pk()), instance_of(Record))

    def test_new_record_is_not_created_if_pk_is_duplicated(self, person_record: Record, client: Client):
        """
        Try to create a new record with duplicated PK. Client should raise exception
        :param person_record:
        :param client:
        """
        person_record.id = None
        assert_that(person_record.id, is_(None))
        # create new record
        person_record = client.records.create(person_record)
        with pytest.raises(RecordAlreadyExistsException):
            client.records.create(person_record)

    def test_record_is_updated(self, person_record: Record, client: Client):
        """
        Change the record`s field value and store this change in the database
        :param person_record:
        :param client:
        """
        person_record.id = None
        assert_that(person_record.id, is_(None))
        person_record = client.records.create(person_record)
        new_name = 'Feodor'
        assert_that(new_name, not_(equal_to(person_record.name)))
        person_record.name = new_name
        person_record = client.records.update(person_record)
        assert_that(person_record.name, equal_to(new_name))

    def test_record_is_deleted(self, person_record: Record, client: Client):
        """
        Delete the record and verify it does not exist in the database
        :param person_record:
        :param client:
        """
        person_record.id = None
        assert_that(person_record.id, is_(None))
        person_record = client.records.create(person_record)
        pk = person_record.get_pk()
        client.records.delete(person_record)
        assert_that(person_record.get_pk(), is_(None))
        assert_that(client.records.get(person_record.obj, pk), is_(None))
