from hamcrest import *

from custodian.objects.fields import NumberField, StringField, BooleanField, RelatedObjectField
from custodian.objects.model import Object


def test_object_serializes_itself():
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
    serialized_object = obj.serialize()
    assert_that(serialized_object, is_(instance_of(dict)))
    assert_that(serialized_object, has_entry('name', obj.name))
    assert_that(serialized_object['fields'][0]['type'], equal_to('number'))


def test_object_with_related_inner_object_field_serializes_itself(person_object):
    obj = Object(
        name='address',
        key='id',
        cas=True,
        fields=[
            NumberField(name='id', optional=True),
            StringField(name='street'),
            BooleanField(name='house'),
            RelatedObjectField(
                name='person',
                obj=person_object,
                link_type=RelatedObjectField.LINK_TYPES.INNER
            )
        ]
    )
    serialized_object = obj.serialize()
    assert_that(serialized_object, is_(instance_of(dict)))
    expected_serialized_field = {'name': 'person', 'type': 'object', 'optional': False, 'linkMeta': 'person',
                                 'linkType': 'inner'}
    assert_that(serialized_object['fields'][3], equal_to(expected_serialized_field))


def test_object_with_related_outer_object_field_serializes_itself(person_object):
    obj = Object(
        name='address',
        key='id',
        cas=True,
        fields=[
            NumberField(name='id', optional=True),
            StringField(name='street'),
            BooleanField(name='house'),
            RelatedObjectField(
                name='persons',
                obj=person_object,
                link_type=RelatedObjectField.LINK_TYPES.OUTER,
                many=True
            )
        ]
    )
    serialized_object = obj.serialize()
    assert_that(serialized_object, is_(instance_of(dict)))
    expected_serialized_field = {'name': 'persons', 'type': 'array', 'optional': False, 'linkMeta': 'person',
                                 'linkType': 'outer'}
    assert_that(serialized_object['fields'][3], equal_to(expected_serialized_field))
