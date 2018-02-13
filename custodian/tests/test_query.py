from hamcrest import *

from custodian.objects.model import Object
from custodian.records.query import Q, Query


def test_q():
    """
    Tests regular Q-expression`s string representation
    """
    queryset = (Q(age__gt=18) | Q(age__lt=53)) & Q(is_active__eq=True)
    assert_that(queryset.to_string(), equal_to('and(or(gt(age, 18), lt(age, 53)), eq(is_active, True))'))


def test_inverted_q():
    """
    Tests Q-expression`s string representation when using the "~" operator
    """
    queryset = (Q(age__gt=18) | Q(age__lt=53)) & ~Q(is_active__eq=True)
    assert_that(queryset.to_string(), equal_to('and(or(gt(age, 18), lt(age, 53)), not(eq(is_active, True)))'))


def test_query(person_object: Object):
    query = Query(person_object).filter((Q(age__gt=18) | Q(age__lt=53)) & Q(is_active__eq=True)) \
        .filter(address__city__name__eq='St. Petersburg')
    assert_that(
        query.to_string(),
        equal_to('and(and(or(gt(age, 18), lt(age, 53)), eq(is_active, True)), eq(address.city.name, St. Petersburg))')
    )
