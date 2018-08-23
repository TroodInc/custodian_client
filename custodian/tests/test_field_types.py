from custodian.client import Client
from custodian.objects import Object
from custodian.objects.fields import NumberField
from custodian.records.model import Record

from hamcrest import *


def test_numeric_field_type_casting(client: Client):
    test_object = Object(
        name="TestObject",
        cas=False,
        fields=[
            NumberField(name='id'),
            NumberField(name='price')
        ],
        key='id',
        objects_manager=client.objects
    )

    test_record = Record(test_object, id=2, price=100.0)

    assert_that(test_record.id, instance_of(int))
    assert_that(test_record.price, instance_of(float))
