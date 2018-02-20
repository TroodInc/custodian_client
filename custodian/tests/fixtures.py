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
