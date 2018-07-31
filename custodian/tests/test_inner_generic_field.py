from hamcrest import *

from custodian.objects import Object
from custodian.objects.fields import NumberField, GenericField, LINK_TYPES


def test_inner_generic_field_serialization(client):
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
        name='person',
        key='id',
        cas=True,
        fields=[
            NumberField(name='id', optional=True),
            GenericField(name='target_object', link_type=LINK_TYPES.INNER, objs=[object_a])
        ],
        objects_manager=client.objects
    )

    serialized_object_b = object_b.serialize()
    assert_that(serialized_object_b["fields"][1], has_entry("linkMetaList", [object_a.name]))
    assert_that(serialized_object_b["fields"][1], has_entry("type", "generic"))
    assert_that(serialized_object_b["fields"][1], has_entry("name", "target_object"))


def test_outer_generic_field_serialization(client):
    object_a = Object(
        name='a',
        fields=[
            NumberField(name='id'),
            GenericField(name='target_object', link_type=LINK_TYPES.INNER, objs=[])
        ],
        key='id',
        cas=False,
        objects_manager=client.objects
    )

    object_b = Object(
        name='person',
        key='id',
        cas=True,
        fields=[
            NumberField(name='id', optional=True),
            GenericField(name='a_set', link_type=LINK_TYPES.OUTER, obj=object_a,
                         outer_link_field="target_object")
        ],
        objects_manager=client.objects
    )
    object_a.fields["target_object"].objs = [object_b]

    serialized_object_b = object_b.serialize()
    assert_that(serialized_object_b["fields"][1], has_entry("linkMeta", object_a.name))
    assert_that(serialized_object_b["fields"][1], has_entry("type", "generic"))
    assert_that(serialized_object_b["fields"][1], has_entry("name", "a_set"))
    assert_that(serialized_object_b["fields"][1], has_entry("outerLinkField", "target_object"))
