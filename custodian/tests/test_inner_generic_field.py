import pytest
from hamcrest import *

from custodian.client import Client
from custodian.objects import Object
from custodian.objects.fields import NumberField, GenericField, LINK_TYPES
from custodian.records.model import Record


@pytest.mark.usefixtures('flush_database')
class TestInnerGenericFieldSchemaLevelSeries:
    def test_inner_generic_field_serialization(self, client: Client):
        object_a = Object(
            name='a',
            fields=[
                NumberField(name='id')
            ],
            key='id',
            cas=False,
            objects_manager=client.objects
        )
        object_b = Object(
            name='b',
            key='id',
            cas=False,
            fields=[
                NumberField(name='id', optional=True),
                GenericField(name='target_object', link_type=LINK_TYPES.INNER, objs=[object_a])
            ],
            objects_manager=client.objects
        )
        object_b.fields["target_object"].objs = [object_a]

        object_a_with_manually_set_b_set = Object(
            name='a',
            fields=[
                NumberField(name='id'),
                GenericField(
                    name='b_set',
                    link_type=LINK_TYPES.OUTER,
                    obj=object_b,
                    outer_link_field='target_object'
                )
            ],
            key='id',
            cas=False,
            objects_manager=client.objects
        )

        serialized_object_b = object_b.serialize()
        assert_that(serialized_object_b["fields"][1], has_entry("linkMetaList", [object_a.name]))
        assert_that(serialized_object_b["fields"][1], has_entry("type", "generic"))
        assert_that(serialized_object_b["fields"][1], has_entry("name", "target_object"))

        client.objects.create(object_a)
        client.objects.create(object_b)
        client.objects.update(object_a_with_manually_set_b_set)

    def test_outer_generic_field_serialization(self, client: Client):
        object_a = client.objects.get('a')
        serialized_object_a = object_a.serialize()
        assert_that(serialized_object_a["fields"][1], has_entry("linkMeta", "b"))
        assert_that(serialized_object_a["fields"][1], has_entry("type", "generic"))
        assert_that(serialized_object_a["fields"][1], has_entry("name", "b_set"))
        assert_that(serialized_object_a["fields"][1], has_entry("outerLinkField", "target_object"))

    def test_generic_inner_field_reflection(self, client: Client):
        retrieved_object_b = client.objects.get("b")
        assert_that(retrieved_object_b.fields["target_object"].objs, has_length(1))
        assert_that(retrieved_object_b.fields["target_object"].objs[0].name, equal_to("a"))
        assert_that(retrieved_object_b.fields["target_object"].link_type, equal_to(LINK_TYPES.INNER))
        assert_that(retrieved_object_b.fields["target_object"].type, equal_to(GenericField.type))

    def test_generic_outer_field_reflection(self, client: Client):
        retrieved_object_b = client.objects.get("a")
        assert_that(retrieved_object_b.fields["b_set"].obj.name, equal_to('b'))
        assert_that(retrieved_object_b.fields["b_set"].link_type, equal_to(LINK_TYPES.OUTER))
        assert_that(retrieved_object_b.fields["b_set"].type, equal_to(GenericField.type))
        assert_that(retrieved_object_b.fields["b_set"].outer_link_field, equal_to('target_object'))


@pytest.mark.usefixtures('flush_database')
class TestInnerGenericFieldRecordLevelSeries:
    def test_field_value_creation_and_retrieving(self, client: Client):
        object_a = Object(
            name='a',
            fields=[
                NumberField(name='id', optional=True, default={'func': 'nextval'})
            ],
            key='id',
            cas=False,
            objects_manager=client.objects
        )
        object_b = Object(
            name='b',
            key='id',
            cas=False,
            fields=[
                NumberField(name='id', optional=True, default={'func': 'nextval'}),
                GenericField(name='target_object', link_type=LINK_TYPES.INNER, objs=[object_a])
            ],
            objects_manager=client.objects
        )
        object_a_with_manually_set_b_set = Object(
            name='a',
            fields=[
                NumberField(name='id', optional=True, default={'func': 'nextval'}),
                GenericField(
                    name='b_set',
                    link_type=LINK_TYPES.OUTER,
                    obj=object_b,
                    outer_link_field='target_object',
                    optional=True
                )
            ],
            key='id',
            cas=False,
            objects_manager=client.objects
        )

        client.objects.create(object_a)
        client.objects.create(object_b)
        client.objects.update(object_a_with_manually_set_b_set)
        # reload A object, because it has been updated with outer generic field
        object_a = client.objects.get(object_a.name)
        a_record = Record(object_a)
        a_record = client.records.create(a_record)
        b_record = Record(object_b, target_object={"_object": "a", "id": a_record.id})
        b_record = client.records.create(b_record)
        # check inner value
        assert_that(b_record.target_object, instance_of(dict))
        assert_that(b_record.target_object, instance_of(dict))
        assert_that(b_record.target_object["_object"], equal_to("a"))
        assert_that(b_record.target_object["id"], a_record.id)
        # check outer value
        # reload A record
        a_record = client.records.query(object_a).filter(id__eq=a_record.id)[0]
        assert_that(a_record.b_set, instance_of(list))
        assert_that(a_record.b_set, has_length(1))
        assert_that(int(a_record.b_set[0]), equal_to(b_record.id))
