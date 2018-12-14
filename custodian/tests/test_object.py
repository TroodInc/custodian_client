import pytest
from hamcrest import *

from custodian.client import Client
from custodian.exceptions import ObjectUpdateException
from custodian.objects import Object
from custodian.objects.fields import NumberField, StringField, BooleanField, RelatedObjectField, LINK_TYPES, \
    ObjectsField


def test_object_serializes_itself(client):
    obj = Object(
        name='person',
        key='id',
        cas=True,
        fields=[
            NumberField(name='id', optional=True),
            StringField(name='name'),
            BooleanField(name='is_active')
        ],
        objects_manager=client.objects
    )
    serialized_object = obj.serialize()
    assert_that(serialized_object, is_(instance_of(dict)))
    assert_that(serialized_object, has_entry('name', obj.name))
    assert_that(serialized_object['fields'][0]['type'], equal_to('number'))


def test_object_with_related_inner_object_field_serializes_itself(person_object, client):
    obj = Object(
        name='address',
        key='id',
        cas=True,
        fields=[
            NumberField(name='id', optional=True),
            StringField(name='street'),
            RelatedObjectField(
                name='person',
                obj=person_object,
                link_type=LINK_TYPES.INNER
            )
        ],
        objects_manager=client.objects
    )
    serialized_object = obj.serialize()
    assert_that(serialized_object, is_(instance_of(dict)))
    expected_serialized_field = {'name': 'person', 'type': 'object', 'optional': False, 'linkMeta': 'person',
                                 'linkType': 'inner'}
    assert_that(serialized_object['fields'][2], equal_to(expected_serialized_field))


def test_object_with_related_outer_object_field_serializes_itself(client):
    address_object = Object(
        name='address',
        key='id',
        cas=True,
        fields=[
            NumberField(name='id', optional=True),
            StringField(name='street')
        ],
        objects_manager=client.objects
    )
    person_obj = Object(
        name='person',
        key='id',
        cas=True,
        fields=[
            NumberField(name='id', optional=True),
            StringField(name='street'),
            RelatedObjectField(
                name='addresses',
                obj=address_object,
                outer_link_field='address_id',
                link_type=LINK_TYPES.OUTER,
                many=True
            )
        ],
        objects_manager=client.objects
    )
    serialized_object = person_obj.serialize()
    assert_that(serialized_object, is_(instance_of(dict)))
    expected_serialized_field = {'name': 'addresses', 'type': 'array', 'optional': False, 'linkMeta': 'address',
                                 'linkType': 'outer', 'outerLinkField': 'address_id'}
    assert_that(serialized_object['fields'][2], equal_to(expected_serialized_field))


def test_improper_object_operations_cause_custodian_error(client: Client, flush_database):
    assert_that(client.objects.get_all(), has_length(0))
    person_obj = Object(
        name='person',
        key='id',
        cas=False,
        fields=[
            NumberField(name='id', optional=True, default={'func': 'nextval'}),
            StringField(name='street')
        ],
        objects_manager=client.objects
    )
    client.objects.create(person_obj)
    assert_that(client.objects.get_all(), has_length(1))
    with pytest.raises(ObjectUpdateException) as error:
        person_obj = Object(
            name='person',
            key='id',
            cas=False,
            fields=[
                NumberField(name='id', optional=True),
                StringField(name='street')
            ],
            objects_manager=client.objects
        )
        client.objects.update(person_obj)
    assert_that(error.value.args[0], contains_string('cannot drop sequence'))
