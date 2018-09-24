from hamcrest import *

from custodian.client import Client
from custodian.objects import Object
from custodian.records.model import Record


def test_client_updates_record_with_partial_data(existing_person_object: Object, client: Client):
    record = Record(obj=existing_person_object, id=23, age=20, name='Ivan', is_active=True, street="Street")
    record = client.records.create(record=record)
    assert_that(record, instance_of(Record))

    # perform partial update
    record = client.records.partial_update(existing_person_object, record.get_pk(), {'name': 'Petr'})
    assert_that(record.name, equal_to('Petr'))

    # check that new data got stored in Custodian
    record = client.records.get(existing_person_object, record.get_pk())
    assert_that(record.name, equal_to('Petr'))
