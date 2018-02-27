import os
import pytest

from custodian.client import Client
from custodian.objects.fields import NumberField, StringField, BooleanField, IntegerField
from custodian.objects import Object
from custodian.records.model import Record


@pytest.fixture(scope='session')
def client():
    return Client(server_url=os.environ['SERVER_URL'])


@pytest.fixture
def person_object(client):
    return Object(
        name='person',
        key='id',
        cas=False,
        fields=[
            IntegerField(name='id', optional=True, default={'func': 'nextval'}),
            StringField(name='name'),
            NumberField(name='age'),
            BooleanField(name='is_active')
        ],
        objects_manager=client.objects
    )


@pytest.fixture
def person_record(person_object):
    return Record(obj=person_object, id=23, age=20, name='Ivan', is_active=True)


@pytest.fixture()
def two_records(client, person_object):
    client.records.bulk_delete(*[x for x in client.records.query(person_object)])
    first_record = Record(obj=person_object, **{'name': 'Feodor', 'is_active': True, 'age': 20})
    second_record = Record(obj=person_object, **{'name': 'Victor', 'is_active': False, 'age': 40})
    client.records.bulk_create(first_record, second_record)
    return first_record, second_record
