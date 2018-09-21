import pytest
from hamcrest import *

from custodian.client import Client
from custodian.objects import Object, Action, METHODS
from custodian.objects.fields import NumberField


@pytest.mark.usefixtures('flush_database')
class TestInnerActionsSeries:
    def test_actions_serialization(self, client: Client):
        object_a = Object(
            name='a',
            fields=[
                NumberField(name='id')
            ],
            key='id',
            cas=False,
            objects_manager=client.objects,
            actions=[Action(method=METHODS.CREATE, protocol='REST', args=["http://localhost/"],
                            include_values={'a': 'b.c.name'})]
        )
        serialized_object = object_a.serialize()
        assert_that(serialized_object['actions'], has_length(1))
        assert_that(serialized_object['actions'][0]['method'], equal_to(METHODS.CREATE))
        assert_that(serialized_object['actions'][0]['protocol'], equal_to('REST'))
        assert_that(serialized_object['actions'][0]['args'], has_length(1))
        assert_that(serialized_object['actions'][0]['includeValues'], has_length(1))

        client.objects.create(object_a)

    def test_actions_reflection(self, client: Client):
        object_a = client.objects.get('a')
        assert_that(object_a.actions, has_length(1))

        assert_that(object_a.actions[0].method, equal_to(METHODS.CREATE))
        assert_that(object_a.actions[0].protocol, equal_to('REST'))
        assert_that(object_a.actions[0].args, has_length(1))
        assert_that(object_a.actions[0].include_values, has_length(1))
