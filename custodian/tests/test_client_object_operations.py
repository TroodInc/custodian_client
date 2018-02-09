import pytest
import requests_mock
from hamcrest import *

from custodian.client import Client
from custodian.exceptions import CommandExecutionFailureException
from custodian.objects.model import Object


def test_client_raises_exception_on_failed_api_call(default_object: Object):
    client = Client(server_url='http://mocked/custodian')
    with pytest.raises(CommandExecutionFailureException):
        with requests_mock.Mocker() as mocker:
            mocker.post('http://mocked/custodian/meta', json={'status': 'Fail'})
            client.objects.create(default_object)


def test_client_makes_correct_request_on_object_creation(default_object: Object):
    client = Client(server_url='http://mocked/custodian')
    with requests_mock.Mocker() as mocker:
        mocker.post('http://mocked/custodian/meta', json={'status': 'OK'})
        obj = client.objects.create(default_object)
        assert_that(obj, is_(instance_of(Object)))


def test_client_makes_correct_request_on_object_update(default_object: Object):
    client = Client(server_url='http://mocked/custodian')
    with requests_mock.Mocker() as mocker:
        mocker.put('http://mocked/custodian/meta/{}'.format(default_object.name), json={'status': 'OK'})
        obj = client.objects.update(default_object)
        assert_that(obj, is_(instance_of(Object)))


def test_client_makes_correct_request_on_object_delete(default_object: Object):
    client = Client(server_url='http://mocked/custodian')
    with requests_mock.Mocker() as mocker:
        mocker.delete('http://mocked/custodian/meta/{}'.format(default_object.name), json={'status': 'OK'})
        obj = client.objects.delete(default_object)
        assert_that(obj, is_(instance_of(Object)))


def test_client_retrieves_existing_object(default_object: Object):
    client = Client(server_url='http://mocked/custodian')
    with requests_mock.Mocker() as mocker:
        mocker.get(
            'http://mocked/custodian/meta/{}'.format(default_object.name),
            json={'status': 'OK', 'data': default_object.serialize()}
        )
        obj = client.objects.get(default_object.name)
        assert_that(obj, is_(instance_of(Object)))
        assert_that(default_object.serialize(), equal_to(obj.serialize()))
