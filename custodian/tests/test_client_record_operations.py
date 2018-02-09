import requests_mock
from hamcrest import *

from custodian.client import Client
from custodian.records.model import Record


def test_client_retrieves_existing_record(person_record: Record):
    client = Client(server_url='http://mocked/custodian')
    with requests_mock.Mocker() as mocker:
        mocker.get(
            'http://mocked/custodian/meta/{}/{}'.format(person_record.obj.name, person_record.id),
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
            'http://mocked/custodian/meta/{}/{}'.format(person_record.obj.name, person_record.id),
            json={
                'status': 'FAIL',
                'data': {}
            }
        )
        record = client.records.get(person_record.obj, person_record.id)
        assert_that(record, is_(None))
