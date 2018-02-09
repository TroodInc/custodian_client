import requests_mock
from hamcrest import *

from custodian.client import Client
from custodian.records.model import Record


def test_client_retrieves_existing_record(person_record: Record):
    client = Client(server_url='http://mocked/custodian')
    with requests_mock.Mocker() as mocker:
        mocker.get(
            'http://mocked/custodian/data/single/{}/{}'.format(person_record.obj.name, person_record.id),
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
            'http://mocked/custodian/data/single/{}/{}'.format(person_record.obj.name, person_record.id),
            json={
                'status': 'FAIL',
                'data': {}
            }
        )
        record = client.records.get(person_record.obj, person_record.id)
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
