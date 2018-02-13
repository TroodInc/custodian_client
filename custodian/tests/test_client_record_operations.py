import requests_mock
from hamcrest import *

from custodian.client import Client
from custodian.objects.model import Object
from custodian.records.model import Record


def test_client_retrieves_existing_record(person_record: Record):
    client = Client(server_url='http://mocked/custodian')
    with requests_mock.Mocker() as mocker:
        mocker.get(
            'http://mocked/custodian/data/single/{}/{}'.format(person_record.obj.name, person_record.get_pk()),
            json={
                'status': 'OK',
                'data': person_record.serialize()
            }
        )
        record = client.records.get(person_record.obj, person_record.id)
        assert_that(record, is_(instance_of(Record)))


def test_client_returns_none_for_nonexistent_record(person_record: Record):
    client = Client(server_url='http://mocked/custodian')
    with requests_mock.Mocker() as mocker:
        mocker.get(
            'http://mocked/custodian/data/single/{}/{}'.format(person_record.obj.name, person_record.get_pk()),
            json={
                'status': 'FAIL',
                'data': {}
            }
        )
        record = client.records.get(person_record.obj, person_record.get_pk())
        assert_that(record, is_(None))


def test_client_returns_new_record_on_record_creation(person_record: Record):
    person_record.id = None
    assert_that(person_record.exists(), is_not(True))
    client = Client(server_url='http://mocked/custodian')
    record_data = person_record.serialize()
    record_data['id'] = 45
    with requests_mock.Mocker() as mocker:
        mocker.post(
            'http://mocked/custodian/data/single/{}'.format(person_record.obj.name),
            json={
                'status': 'OK',
                'data': record_data
            }
        )
        record = client.records.create(person_record)
        assert_that(record, is_(instance_of(Record)))
        assert_that(record.exists())
        assert_that(record.id, equal_to(45))


def test_client_deletes(person_record: Record):
    assert_that(person_record.exists())
    client = Client(server_url='http://mocked/custodian')
    record_data = person_record.serialize()
    with requests_mock.Mocker() as mocker:
        mocker.delete(
            'http://mocked/custodian/data/single/{}/{}'.format(person_record.obj.name, person_record.get_pk()),
            json={
                'status': 'OK',
                'data': record_data
            }
        )
        client.records.delete(person_record)
        assert_that(person_record.exists(), is_not(True))


def test_client_returns_updated_record_on_record_update(person_record: Record):
    client = Client(server_url='http://mocked/custodian')
    record_data = person_record.serialize()
    record_data['is_active'] = False
    with requests_mock.Mocker() as mocker:
        mocker.put(
            'http://mocked/custodian/data/single/{}/{}'.format(person_record.obj.name, person_record.get_pk()),
            json={
                'status': 'OK',
                'data': record_data
            }
        )
        record = client.records.update(person_record)
        assert_that(record, is_(instance_of(Record)))
        assert_that(record.exists())
        assert_that(record.is_active, is_(False))


def test_client_returns_iterable_of_records_on_bulk_query(person_object: Object, person_record: Record):
    client = Client(server_url='http://mocked/custodian')
    query = client.records.query(person_object).filter(address__city_id__eq=45)
    with requests_mock.Mocker() as mocker:
        mocker.get(
            'http://mocked/custodian/data/bulk/{}'.format(person_object.name),
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


def test_client_returns_list_of_records_on_bulk_create(person_object: Object):
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

    client = Client(server_url='http://mocked/custodian')
    with requests_mock.Mocker() as mocker:
        mocker.post(
            'http://mocked/custodian/data/bulk/{}'.format(person_object.name),
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


def test_client_returns_list_of_records_on_bulk_update(person_object: Object):
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

    client = Client(server_url='http://mocked/custodian')
    with requests_mock.Mocker() as mocker:
        mocker.put(
            'http://mocked/custodian/data/bulk/{}'.format(person_object.name),
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


def test_client_returns_list_of_records_without_pk_value_on_bulk_delete(person_object: Object):
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

    client = Client(server_url='http://mocked/custodian')
    with requests_mock.Mocker() as mocker:
        mocker.delete(
            'http://mocked/custodian/data/bulk/{}'.format(person_object.name),
            json={
                'status': 'OK'
            }
        )
        client.records.bulk_delete(*records_to_delete)
        for record in records_to_delete:
            assert_that(not record.exists())
