import pytest
import requests_mock
from hamcrest import *

from custodian.client import Client
from custodian.exceptions import CommandExecutionFailureException
from custodian.objects.fields import NumberField, StringField, BooleanField
from custodian.objects.model import Object


def test_client_makes_correct_request_on_object_creation():
    client = Client(server_url='http://mocked/custodian')
    obj = Object(
        name='person',
        key='id',
        cas=True,
        fields=[
            NumberField(name='id', optional=True),
            StringField(name='name'),
            BooleanField(name='is_active')
        ]
    )
    with requests_mock.Mocker() as mocker:
        mocker.post('http://mocked/custodian/meta', json={'status': 'OK'})
        obj = client.objects.create(obj)
        assert_that(obj, is_(instance_of(Object)))


def test_client_raises_exception_on_failed_api_call():
    client = Client(server_url='http://mocked/custodian')
    obj = Object(
        name='person',
        key='id',
        cas=True,
        fields=[
            NumberField(name='id', optional=True),
            StringField(name='name'),
            BooleanField(name='is_active')
        ]
    )
    with pytest.raises(CommandExecutionFailureException):
        with requests_mock.Mocker() as mocker:
            mocker.post('http://mocked/custodian/meta', json={'status': 'Fail'})
            client.objects.create(obj)
