import pytest
import requests_mock
from hamcrest import *

from custodian.client import Client
from custodian.exceptions import CommandExecutionFailureException
from custodian.objects import Object


def test_client_raises_exception_on_failed_api_call(person_object: Object, client: Client):
    with pytest.raises(CommandExecutionFailureException):
        with requests_mock.Mocker() as mocker:
            mocker.post('http://mocked/custodian/meta', json={'status': 'Fail'})
            client.objects.create(person_object)


def test_client_makes_correct_request_on_object_creation(person_object: Object, client: Client):
    obj = client.objects.create(person_object)
    assert_that(obj, is_(instance_of(Object)))


def test_client_makes_correct_request_on_object_update(person_object: Object):
    client = Client(server_url='http://mocked/custodian')
    with requests_mock.Mocker() as mocker:
        mocker.put('http://mocked/custodian/meta/{}'.format(person_object.name), json={'status': 'OK'})
        obj = client.objects.update(person_object)
        assert_that(obj, is_(instance_of(Object)))


def test_client_makes_correct_request_on_object_delete(person_object: Object):
    client = Client(server_url='http://mocked/custodian')
    with requests_mock.Mocker() as mocker:
        mocker.delete('http://mocked/custodian/meta/{}'.format(person_object.name), json={'status': 'OK'})
        obj = client.objects.delete(person_object)
        assert_that(obj, is_(instance_of(Object)))


def test_client_retrieves_existing_object(person_object: Object):
    client = Client(server_url='http://mocked/custodian')
    with requests_mock.Mocker() as mocker:
        mocker.get(
            'http://mocked/custodian/meta/{}'.format(person_object.name),
            json={'status': 'OK', 'data': person_object.serialize()}
        )
        obj = client.objects.get(person_object.name)
        assert_that(obj, is_(instance_of(Object)))
        assert_that(person_object.serialize(), equal_to(obj.serialize()))
