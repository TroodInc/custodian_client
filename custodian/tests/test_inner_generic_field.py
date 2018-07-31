from hamcrest import *

from custodian.client import Client
from custodian.objects import Object
from custodian.objects.fields import NumberField, GenericField, LINK_TYPES


class TestInngerGenericFieldSeries:
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

        serialized_object_b = object_b.serialize()
        assert_that(serialized_object_b["fields"][1], has_entry("linkMetaList", [object_a.name]))
        assert_that(serialized_object_b["fields"][1], has_entry("type", "generic"))
        assert_that(serialized_object_b["fields"][1], has_entry("name", "target_object"))

        client.objects.create(object_a)
        client.objects.create(object_b)

    def test_outer_generic_field_serialization(self, client: Client):
        object_a = client.objects.get('a')
        serialized_object_b = object_a.serialize()
        assert_that(serialized_object_b["fields"][1], has_entry("linkMeta", "b"))
        assert_that(serialized_object_b["fields"][1], has_entry("type", "generic"))
        assert_that(serialized_object_b["fields"][1], has_entry("name", "b__set"))
        assert_that(serialized_object_b["fields"][1], has_entry("outerLinkField", "target_object"))

    def test_generic_inner_field_reflection(self, client: Client):
        retrieved_object_b = client.objects.get("b")
        assert_that(retrieved_object_b.fields["target_object"].objs, has_length(1))
        assert_that(retrieved_object_b.fields["target_object"].objs[0].name, equal_to("a"))
        assert_that(retrieved_object_b.fields["target_object"].link_type, equal_to(LINK_TYPES.INNER))
        assert_that(retrieved_object_b.fields["target_object"].type, equal_to(GenericField.type))

    def test_generic_outer_field_reflection(self, client: Client):
        retrieved_object_b = client.objects.get("a")
        assert_that(retrieved_object_b.fields["b__set"].obj.name, equal_to('b'))
        assert_that(retrieved_object_b.fields["b__set"].link_type, equal_to(LINK_TYPES.OUTER))
        assert_that(retrieved_object_b.fields["b__set"].type, equal_to(GenericField.type))
        assert_that(retrieved_object_b.fields["b__set"].outer_link_field, equal_to('target_object'))
