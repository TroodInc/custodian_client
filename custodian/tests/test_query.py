import pytest
from hamcrest import *

from custodian.client import Client
from custodian.exceptions import QueryException
from custodian.objects.model import Object
from custodian.records.query import Q, Query


def test_q():
    """
    Tests regular Q-expression`s string representation
    """
    queryset = (Q(age__gt=18) | Q(age__lt=53)) & Q(is_active__eq=True)
    assert_that(queryset.to_string(), equal_to('and(or(gt(age, 18), lt(age, 53)), eq(is_active, True))'))


def test_q_with_list_value():
    """
    Tests regular Q-expression`s string representation with a list as a value
    """
    queryset = Q(city_id__in=[1, 4, 7])
    assert_that(queryset.to_string(), equal_to('in(city_id, (1, 4, 7))'))


def test_q_unknown_operator_raises_exception():
    """
    Tests regular Q-expression`s string representation
    """
    queryset = (Q(age__gt=18) | Q(age__lt=53)) & Q(is_active__custom_operator=True)
    with pytest.raises(QueryException):
        queryset.to_string()


def test_inverted_q():
    """
    Tests Q-expression`s string representation when using the "~" operator
    """
    queryset = (Q(age__gt=18) | Q(age__lt=53)) & ~Q(is_active__eq=True)
    assert_that(queryset.to_string(), equal_to('and(or(gt(age, 18), lt(age, 53)), not(eq(is_active, True)))'))


def test_query(person_object: Object):
    query = Query(person_object, None).filter((Q(age__gt=18) | Q(age__lt=53)) & Q(is_active__eq=True)) \
        .filter(address__city__name__eq='St. Petersburg')
    assert_that(
        query.to_string(),
        equal_to('and(and(or(gt(age, 18), lt(age, 53)), eq(is_active, True)), eq(address.city.name, St. Petersburg))')
    )


def test_query_ordering(person_object: Object):
    query = Query(person_object, None).filter(is_active__eq=True).order_by('person__last_name', '-person__phone_number')
    assert_that(query.to_string(), contains_string('sort(+person.last_name, -person.phone_number)'))


def test_query_slicing(person_object: Object):
    query = Query(person_object, None).filter(is_active__eq=True)[50:100]
    assert_that(query.to_string(), contains_string('limit(50, 50)'))


def test_query_access_by_index(person_object: Object):
    query = Query(person_object, None).filter(is_active__eq=True)[141]
    assert_that(query.to_string(), contains_string('limit(141, 1)'))


def test_query_resets_evaluated_result_on_query_modifications(person_object: Object):
    client = Client(server_url='http://mocked/custodian')
    query = Query(person_object, client.records).filter(is_active__eq=True)
    query._is_evaluated = True
    assert_that(query._is_evaluated)
    query = query.filter(client__first_name__eq='Ivan')
    assert_that(not query._is_evaluated)
