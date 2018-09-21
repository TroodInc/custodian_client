import requests_mock
from hamcrest import *

from custodian.client import Client
from custodian.objects import Object
from custodian.objects.fields import NumberField, StringField, RelatedObjectField, LINK_TYPES


def test_client_makes_correct_request_on_object_creation(person_object: Object, client: Client):
    with requests_mock.Mocker() as mocker:
        mocker.put('/'.join([client.server_url, 'meta']), json={'status': 'OK', 'data': person_object.serialize()})
        mocker.get('/'.join([client.server_url, 'meta', person_object.name]),
                   json={'status': 'OK', 'data': person_object.serialize()})
        client.objects.create(person_object)
        assert_that(person_object, is_(instance_of(Object)))


def test_client_makes_correct_request_on_object_update(person_object: Object, client: Client):
    with requests_mock.Mocker() as mocker:
        mocker.post('/'.join([client.server_url, 'meta/{}'.format(person_object.name)]),
                    json={'status': 'OK', 'data': person_object.serialize()})
        # mock preprocess request
        mocker.get('/'.join([client.server_url, 'meta/{}'.format(person_object.name)]),
                   json={'status': 'OK', 'data': person_object.serialize()})
        obj = client.objects.update(person_object)
        assert_that(obj, is_(instance_of(Object)))


def test_client_makes_correct_request_on_object_delete(person_object: Object):
    client = Client(server_url='http://mocked/custodian')
    with requests_mock.Mocker() as mocker:
        mocker.delete('/'.join([client.server_url, 'meta/{}'.format(person_object.name)]),
                      json={'status': 'OK', 'data': person_object.serialize()})
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


def test_client_retrieves_list_of_objects(client: Client, person_object: Object):
    with requests_mock.Mocker() as mocker:
        mocker.get(
            '/'.join([client.server_url, 'meta/']),
            json={'status': 'OK', 'data': [person_object.serialize()]}
        )
        objs = client.objects.get_all()
        assert_that(objs, has_length(1))
        assert_that(person_object.serialize(), equal_to(objs[0].serialize()))


class TestCustodianIntegrationSeries:
    def test_the_database_contains_not_objects(self, client: Client):
        """
        Remove any existing objects and check the database is empty
        :param client:
        """
        for obj in client.objects.get_all():
            client.objects.delete(obj)
        assert_that(client.objects.get_all(), has_length(0))

    def test_new_object_is_created(self, person_object: Object, client: Client):
        """
        Create a new object and retrieve it from the database
        :param person_object:
        :param client:
        """
        # create new object
        client.objects.create(person_object)
        # retrieve this object from the Custodian
        retrieved_person_obj = client.objects.get(person_object.name)
        assert_that(retrieved_person_obj, instance_of(Object))

    def test_object_is_updated(self, person_object: Object, client: Client):
        """
        Add a new field to an existing object and extract the object from the database to verify that the field has
        been added
        :param person_object:
        :param client:
        """
        assert_that('last_name' not in person_object.fields.keys())

        person_object.fields['last_name'] = StringField(name='last_name')
        client.objects.update(person_object)
        retrieved_person_obj = client.objects.get(person_object.name)
        assert_that(retrieved_person_obj.fields, has_key('last_name'))

    def test_related_object_is_created(self, person_object: Object, client: Client):
        """
        Create a new object, which has a foreign key to the Person object
        :param person_object:
        :param client:
        """
        account_object = Object(
            name='account',
            fields=[
                NumberField(name='id'),
                StringField(name='number'),
                RelatedObjectField(
                    name='person',
                    obj=person_object,
                    link_type=LINK_TYPES.INNER
                )
            ],
            key='id',
            cas=False,
            objects_manager=client.objects
        )
        client.objects.create(account_object)
        account_object = client.objects.get(account_object.name)
        assert_that(account_object, instance_of(Object))
        assert_that(account_object.fields['person'], instance_of(RelatedObjectField))

    def test_object_is_deleted(self, person_object: Object, client: Client):
        """
        Remove the object from the database and verify it not longer exists in the database
        :param client:
        """
        account_object = Object(
            name='account',
            fields=[
                NumberField(name='id'),
                StringField(name='number'),
                RelatedObjectField(
                    name='person',
                    obj=person_object,
                    link_type=LINK_TYPES.INNER
                )
            ],
            key='id',
            cas=False,
            objects_manager=client.objects
        )
        assert_that(client.objects.get('account'), instance_of(Object))
        client.objects.delete(account_object)
        assert_that(client.objects.get(account_object.name), is_(None))
