import os

import pytest
from hamcrest import *

from custodian.client import Client
from custodian.exceptions import ObjectDeletionException
from custodian.objects import Object
from custodian.objects.fields import NumberField, StringField, BooleanField, IntegerField
from custodian.records.model import Record


@pytest.fixture(scope='session')
def client():
    return Client(server_url=os.environ['SERVER_URL'])


@pytest.fixture(scope='session')
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


@pytest.fixture
def two_records(client, existing_person_object):
    client.records.bulk_delete(*[x for x in client.records.query(existing_person_object)])
    first_record = Record(obj=existing_person_object, **{'name': 'Feodor', 'is_active': True, 'age': 20})
    second_record = Record(obj=existing_person_object, **{'name': 'Victor', 'is_active': False, 'age': 40})
    client.records.bulk_create(first_record, second_record)
    return first_record, second_record


@pytest.fixture(scope='class')
def flush_database(client):
    """
    Remove all objects from the database
    """
    for _ in range(0, 3):
        # repeat 2 times to guarantee all objects are deleted
        for obj in client.objects.get_all():
            try:
                client.objects.delete(obj)
            except ObjectDeletionException:
                pass
    assert_that(client.objects.get_all(), has_length(0))


@pytest.fixture
def existing_person_object(client, person_object):
    existing_person_object = client.objects.get(person_object.name)
    if not existing_person_object:
        return client.objects.create(person_object)
    else:
        return existing_person_object
