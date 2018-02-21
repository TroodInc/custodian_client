import os
import pytest

from custodian.client import Client
from custodian.objects.fields import NumberField, StringField, BooleanField
from custodian.objects import Object
from custodian.records.model import Record


@pytest.fixture(scope='session')
def client():
    return Client(server_url=os.environ['SERVER_URL'])


@pytest.fixture
def person_object():
    return Object(
        name='person',
        key='id',
        cas=False,
        fields=[
            NumberField(name='id', optional=True, default={'func': 'nextval'}),
            StringField(name='name'),
            BooleanField(name='is_active')
        ]
    )


@pytest.fixture
def person_record(person_object):
    return Record(obj=person_object, id=23, name='Ivan', is_active=True)


@pytest.fixture()
def two_records(client, person_object):
    first_record = Record(obj=person_object, **{'name': 'Feodor', 'is_active': True})
    second_record = Record(obj=person_object, **{'name': 'Victor', 'is_active': False})
    client.records.bulk_create(first_record, second_record)
    return first_record, second_record
