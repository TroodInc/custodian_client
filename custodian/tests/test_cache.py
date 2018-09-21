import copy
import os

import pytest
from hamcrest import *

from custodian.client import Client
from custodian.objects import Object
from custodian.tests.utils import call_counter


@pytest.mark.usefixtures('flush_database')
class TestRqlSeries:
    def test_cache_works_for_get_operation(self, existing_person_object: Object):
        """
        Once meta retrieved from Custodian, it should be returned from cache
        """
        client = Client(server_url=os.environ['SERVER_URL'], use_cache=True)

        client.execute = call_counter(client.execute)

        person_object = client.objects.get(existing_person_object.name)
        assert_that(person_object, instance_of(Object))

        initial_call_count = client.execute.call_count
        re_retrieved_person_object = client.objects.get(existing_person_object.name)
        assert_that(person_object, is_(re_retrieved_person_object))
        assert_that(client.execute.call_count, equal_to(initial_call_count))

    def test_cache_is_flushed_on_object_update(self, existing_person_object: Object):
        """
        Once meta retrieved from Custodian, it should be returned from cache
        """
        client = Client(server_url=os.environ['SERVER_URL'], use_cache=True)

        client.execute = call_counter(client.execute)
        initial_person_object = client.objects.get(existing_person_object.name)
        assert_that(initial_person_object, instance_of(Object))
        initial_call_count = client.execute.call_count

        updated_person_object = copy.deepcopy(existing_person_object)
        del updated_person_object._fields['street']

        # two calls of 'execute'(both for update and get operation) should be done
        client.objects.update(updated_person_object)
        re_retrieved_person_object = client.objects.get(existing_person_object.name)

        assert_that(initial_call_count + 2, equal_to(client.execute.call_count))

        assert_that(re_retrieved_person_object.fields, has_length(len(updated_person_object.fields)))

    def test_cache_is_flushed_on_object_remove(self, existing_person_object: Object):
        """
        Once meta retrieved from Custodian, it should be returned from cache
        """
        client = Client(server_url=os.environ['SERVER_URL'], use_cache=True)

        client.execute = call_counter(client.execute)
        initial_person_object = client.objects.get(existing_person_object.name)
        assert_that(initial_person_object, instance_of(Object))
        client.objects.delete(existing_person_object)
        assert_that(client.objects.get(existing_person_object.name), is_(None))
