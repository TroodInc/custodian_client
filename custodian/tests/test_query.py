import pytest
from hamcrest import *

from custodian.client import Client
from custodian.exceptions import QueryException
from custodian.objects import Object
from custodian.records.query import Q, Query


def test_q():
    """
    Tests regular Q-expression`s string representation
    """
    queryset = (Q(age__gt=18) | Q(age__lt=53)) & Q(is_active__eq=True)
    assert_that(queryset.to_string(), equal_to('and(or(gt(age,18),lt(age,53)),eq(is_active,True))'))


def test_q_with_list_value():
    """
    Tests regular Q-expression`s string representation with a list as a value
    """
    queryset = Q(city_id__in=[1, 4, 7])
    assert_that(queryset.to_string(), equal_to('in(city_id,(1,4,7))'))


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
    assert_that(queryset.to_string(), equal_to('and(or(gt(age,18),lt(age,53)),not(eq(is_active,True)))'))


def test_query(person_object: Object):
    query = Query(person_object, None).filter((Q(age__gt=18) | Q(age__lt=53)) & Q(is_active__eq=True)) \
        .filter(address__city__name__eq='St. Petersburg')
    assert_that(
        query.to_string(),
        equal_to('and(and(or(gt(age,18),lt(age,53)),eq(is_active,True)),eq(address.city.name,St. Petersburg))')
    )


def test_query_ordering(person_object: Object):
    query = Query(person_object, None).filter(is_active__eq=True).order_by('+person__last_name',
                                                                           '-person__phone_number')
    assert_that(query.to_string(), contains_string('sort(+person.last_name, -person.phone_number)'))


def test_query_slicing(person_object: Object):
    query = Query(person_object, None).filter(is_active__eq=True)[150:200]
    assert_that(query.to_string(), contains_string('limit(150,50)'))


def test_query_access_by_index(person_object: Object):
    query = Query(person_object, None).filter(is_active__eq=True)
    query._is_evaluated = True
    query._result = [1, 2, 3, 4, 5]
    assert_that(query[3], equal_to(4))


def test_query_resets_evaluated_result_on_query_modifications(person_object: Object):
    client = Client(server_url='http://mocked/custodian')
    query = Query(person_object, client.records).filter(is_active__eq=True)
    query._is_evaluated = True
    assert_that(query._is_evaluated)
    query = query.filter(client__first_name__eq='Ivan')
    assert_that(not query._is_evaluated)


def test_query_filter_operation_does_not_affect_existing_query(person_object: Object):
    base_query = Query(person_object, None).filter(Q(is_active__eq=True))
    updated_query = base_query.filter(address__city__name__eq='St. Petersburg')
    assert_that(base_query.to_string(), equal_to('eq(is_active,True)'))
    assert_that(updated_query.to_string(), equal_to('and(eq(is_active,True),eq(address.city.name,St. Petersburg))'))


def test_empty_query_with_limits_assembles_correct_expression(person_object: Object):
    base_query = Query(person_object, None)[:100]
    assert_that(base_query.to_string(), equal_to('limit(0,100)'))
