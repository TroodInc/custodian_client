import pytest

from custodian.objects.fields import NumberField, StringField, BooleanField
from custodian.objects import Object
from custodian.records.model import Record


@pytest.fixture
def person_object():
    return Object(
        name='person',
        key='id',
        cas=True,
        fields=[
            NumberField(name='id', optional=True),
            StringField(name='name'),
            BooleanField(name='is_active')
        ]
    )


@pytest.fixture
def person_record(person_object):
    return Record(obj=person_object, id=23, name='Ivan Petrov', is_active=True)
