import pytest
from hamcrest import *

from custodian.client import Client
from custodian.objects import Object
from custodian.objects.fields import NumberField, LINK_TYPES, ObjectsField, StringField
from custodian.records.model import Record


@pytest.mark.usefixtures('flush_database')
class TestObjectsFieldSchemaLevelSeries:
    def test_field_serialization(self, existing_person_object, client):
        address_object = Object(
            name='address',
            key='id',
            cas=False,
            fields=[
                NumberField(name='id', optional=True),
                StringField(name='street'),
                ObjectsField(
                    name='neighbours',
                    obj=existing_person_object,
                    link_type=LINK_TYPES.INNER
                )
            ],
            objects_manager=client.objects
        )
        serialized_object = address_object.serialize()
        assert_that(serialized_object, is_(instance_of(dict)))
        expected_serialized_field = {'name': 'neighbours', 'type': 'objects', 'optional': False,
                                     'linkMeta': 'person', 'linkType': 'inner'}
        assert_that(serialized_object['fields'][2], equal_to(expected_serialized_field))

        client.objects.create(address_object)

    def test_generic_inner_field_reflection(self, client: Client, person_object):
        retrieved_object_b = client.objects.get("address")
        assert_that(retrieved_object_b.fields["neighbours"].obj.name, equal_to(person_object.name))
        assert_that(retrieved_object_b.fields["neighbours"], instance_of(ObjectsField))


@pytest.mark.usefixtures('flush_database')
class TestInnerGenericFieldRecordLevelSeries:
    def setup_objects(self, client):
        if not client.objects.get('a'):
            a_object = Object(
                name='a',
                fields=[
                    NumberField(name='id', optional=True, default={'func': 'nextval'}),
                    StringField(name='name')
                ],
                key='id',
                cas=False,
                objects_manager=client.objects
            )
            b_object = Object(
                name='b',
                key='id',
                cas=False,
                fields=[
                    NumberField(name='id', optional=True, default={'func': 'nextval'}),
                    ObjectsField(name='a_records', link_type=LINK_TYPES.INNER, obj=a_object)
                ],
                objects_manager=client.objects
            )

            self.a_object = client.objects.create(a_object)
            self.b_object = client.objects.create(b_object)
            self.a_record = client.records.create(Record(self.a_object, name="A record"))
        else:
            self.a_object = client.objects.get('a')
            self.b_object = client.objects.get('b')
            self.a_record = client.records.create(Record(self.a_object, name="A record"))

    def test_field_value_creation_and_retrieving_with_nested_record_as_object_and_depth_set_to_1(self, client: Client):
        self.setup_objects(client)
        b_record = Record(self.b_object, a_records=[self.a_record])

        # create and check value with depth set to 1
        b_record_with_depth_set_to_1 = client.records.create(b_record)
        assert_that(b_record_with_depth_set_to_1.a_records, instance_of(list))
        assert_that(b_record_with_depth_set_to_1.a_records, has_length(1))
        assert_that(b_record_with_depth_set_to_1.a_records[0], instance_of(float))

    def test_field_value_creation_and_retrieving_with_nested_record_as_object_and_depth_set_to_2(self, client: Client):
        self.setup_objects(client)
        b_record = Record(self.b_object, a_records=[self.a_record])

        # create and check value with depth set to 2
        b_record_with_depth_set_to_2 = client.records.create(b_record, depth=2)
        assert_that(b_record_with_depth_set_to_2.a_records, instance_of(list))
        assert_that(b_record_with_depth_set_to_2.a_records, has_length(1))
        assert_that(b_record_with_depth_set_to_2.a_records[0], instance_of(Record))

    def test_field_value_serializing_with_nested_record_as_array_of_ids(self, client: Client):
        self.setup_objects(client)
        b_record = Record(self.b_object, a_records=[self.a_record])

        # create and check value with depth set to 1
        b_record_with_depth_set_to_1 = client.records.create(b_record)

        serialized_data = b_record_with_depth_set_to_1.serialize()
        assert_that(serialized_data['a_records'], has_length(1))
        assert_that(serialized_data['a_records'][0], instance_of(float))
