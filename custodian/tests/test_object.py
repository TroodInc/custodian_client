from hamcrest import *

from custodian.objects.fields import NumberField, StringField, BooleanField
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
