import pytest

from custodian.objects.fields import NumberField, StringField, BooleanField
from custodian.objects.model import Object


@pytest.fixture
def default_object():
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
