import pytest
from hamcrest import *

from custodian.client import Client
from custodian.objects import Object
from custodian.objects.fields import NumberField, GenericField, LINK_TYPES, StringField
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
    def setup_objects(self, client):
        if not client.objects.get('a'):
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
                    GenericField(name='target_object', link_type=LINK_TYPES.INNER, objs=[object_a]),
                    StringField(name='name'),
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
            self.object_b = client.objects.create(object_b)
            self.object_a = client.objects.update(object_a_with_manually_set_b_set)

            a_record = Record(self.object_a)
            self.a_record = client.records.create(a_record)
            b_record = Record(self.object_b, target_object={"_object": "a", "id": self.a_record.id}, name="B record")
            self.b_record = client.records.create(b_record)
        else:
            self.object_b = client.objects.get('b')
            self.object_a = client.objects.get('a')
            self.a_record = client.records.query(self.object_a)[0]
            self.b_record = client.records.query(self.object_b)[0]

    def test_field_value_creation_and_retrieving_of_inner(self, client: Client):
        self.setup_objects(client)

        # check inner value
        assert_that(self.b_record.target_object, instance_of(dict))
        assert_that(self.b_record.target_object, instance_of(dict))
        assert_that(self.b_record.target_object["_object"], equal_to("a"))
        assert_that(self.b_record.target_object["id"], self.a_record.id)

    def test_field_value_creation_and_retrieving_of_outer_value_with_depth_depth_set_to_2(self, client: Client):
        self.setup_objects(client)

        # reload A record and check its values with depth set to 2
        a_record = client.records.query(self.object_a, depth=2).filter(id__eq=self.a_record.id)[0]
        assert_that(a_record.b_set, instance_of(list))
        assert_that(a_record.b_set, has_length(1))
        assert_that(a_record.b_set[0], instance_of(Record))
        assert_that(a_record.b_set[0].id, equal_to(self.b_record.id))

    @pytest.mark.xfail
    def test_field_value_creation_and_retrieving_of_outer_value_with_depth_depth_set_to_1(self, client: Client):
        # Fails until TB-192 is fixed
        self.setup_objects(client)

        # reload A record and check its values with depth set to 1
        a_record = client.records.query(self.object_a, depth=1).filter(id__eq=self.a_record.id)[0]
        assert_that(a_record.b_set, instance_of(list))
        assert_that(a_record.b_set, has_length(1))
        assert_that(int(a_record.b_set[0]), equal_to(self.b_record.id))
