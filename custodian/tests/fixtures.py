import os

import pytest

from custodian.client import Client
from custodian.exceptions import ObjectDeletionException
from custodian.objects import Object
from custodian.objects.fields import NumberField, StringField, BooleanField, IntegerField, DateTimeField, GenericField, \
    LINK_TYPES
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
            StringField(name='street'),
            BooleanField(name='is_active'),
            DateTimeField(name='created_at', default={'func': 'now'}, optional=True)
        ],
        objects_manager=client.objects
    )


@pytest.fixture
def task_object(client, person_object):
    return Object(
        name='task',
        key='id',
        cas=False,
        fields=[
            IntegerField(name='id', optional=True, default={'func': 'nextval'}),
            StringField(name='name'),
            GenericField(name='owner', link_type=LINK_TYPES.INNER, objs=[person_object], optional=True)
        ],
        objects_manager=client.objects
    )


@pytest.fixture
def person_record(person_object):
    return Record(obj=person_object, id=23, age=20, name='Ivan', is_active=True, street="Street")


@pytest.fixture
def two_records(client, existing_person_object):
    client.records.bulk_delete(*[x for x in client.records.query(existing_person_object)])
    first_record = Record(obj=existing_person_object,
                          **{'name': 'Feodor', 'is_active': True, 'age': 20, 'street': 'street'})
    second_record = Record(obj=existing_person_object,
                           **{'name': 'Victor', 'is_active': False, 'age': 40, 'street': 'street'})
    first_record, second_record = client.records.bulk_create(first_record, second_record)
    return first_record, second_record


@pytest.fixture(scope='class')
def flush_database(client):
    """
    Remove all objects from the database
    """
    for _ in range(0, 100):
        # repeat 2 times to guarantee all objects are deleted
        objects = client.objects.get_all()
        if len(objects) == 0:
            break
        for obj in objects:
            try:
                client.objects.delete(obj)
            except ObjectDeletionException:
                pass


@pytest.fixture
def existing_person_object(client, person_object):
    existing_person_object = client.objects.get(person_object.name)
    if existing_person_object:
        client.objects.delete(person_object)
    return client.objects.create(person_object)
