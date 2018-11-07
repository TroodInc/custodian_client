from hamcrest import *

from custodian.objects import Object
from custodian.records.model import Record


class TestCustodianBulkOperationsIntegrationSeries:
    def test_record_is_serialized_with_generic_field_value(self, task_object: Object, person_object: Object):
        """
        Create two records and verify pk values are assigned
        :param person_object:
        :param client:
        """

        task_record = Record(
            task_object,
            **{'name': 'Some task', 'owner': {"_object": person_object.name, person_object.key: 5}}
        )
        data = task_record.serialize()
        assert_that(data, instance_of(dict))
        assert_that(data, has_entry('name', 'Some task'))
        assert_that(data, has_entry('owner', {'_object': person_object.name, person_object.key: 5}))

    def test_record_is_serialized_with_null_generic_field_value(self, task_object: Object, person_object: Object):
        """
        Create two records and verify pk values are assigned
        :param person_object:
        :param client:
        """

        task_record = Record(
            task_object,
            **{'name': 'Some task', 'owner': None}
        )
        data = task_record.serialize()
        assert_that(data, instance_of(dict))
        assert_that(data, has_entry('name', 'Some task'))
        assert_that(data, has_entry('owner', None))
