from copy import deepcopy

from custodian.exceptions import QueryException
from custodian.objects.model import Object


class Q:
    _query = None
    _logical_expressions = None
    _inverted = None

    _KNOWN_OPERATORS = ('in', 'like', 'eq', 'ne', 'gt', 'ge', 'lt', 'le')

    def __init__(self, **kwargs):
        self._query = deepcopy(kwargs)
        self._logical_expressions = []
        self._inverted = False

    def __and__(self, other):
        self._logical_expressions.append({
            'operator': 'and',
            'query': other
        })
        return self

    def __or__(self, other):
        self._logical_expressions.append({
            'operator': 'or',
            'query': other
        })
        return self

    def __invert__(self):
        self._inverted = not self._inverted
        return self

    def to_string(self):
        """
        Constructs a string representation of RQL query
        :return:
        """
        # construct query first
        expressions = []
        for key, value in self._query.items():
            operator, field = self._parse_key(key)
            expressions.append('{}({}, {})'.format(operator, field, value))
        query_string = ', '.join(expressions)
        # and then apply logical operators
        for logical_expression in self._logical_expressions:
            query_string = '{}({}, {})'.format(
                logical_expression['operator'], query_string, logical_expression['query'].to_string()
            )
        # apply inversion operator
        if self._inverted:
            query_string = 'not({})'.format(query_string)
        return query_string

    def _parse_key(self, key):
        """
        Parses the key to a field and an operator.
        Example: person__age__gt will be parsed to the "person.age" field and the "gt" operator
        :param key:
        :return:
        """
        split_key = key.split('__')
        operator = split_key[-1]
        field = '.'.join(split_key[:-1])
        if operator not in self._KNOWN_OPERATORS:
            raise QueryException('"{}" operator is unknown'.format(operator))
        return operator, field


def mark_as_unevaluated(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        self = args[0]
        # mark as unevaluated only if no exception was raised
        self._is_evaluated = False
        self._result = None
        return result

    return wrapper


def evaluate(func):
    def wrapper(*args, **kwargs):
        self = args[0]
        if not self._is_evaluated:
            self._evaluate()
        return func(*args, **kwargs)

    return wrapper


class Query:
    _q_objects = None
    _orderings = None
    _limit = None
    _is_evaluated = None
    _result = None

    def __init__(self, obj: Object, manager):
        self._obj = obj
        self._manager = manager
        self._q_objects = []
        self._orderings = []
        self._limit = None
        self._is_evaluated = False
        self._result = None

    @mark_as_unevaluated
    def filter(self, q_object: Q = None, **kwargs):
        """
        Applies filters to the current query
        :param q_object:
        :param kwargs:
        :return:
        """
        if q_object:
            self._q_objects.append(q_object)
        if kwargs:
            self._q_objects.append(Q(**kwargs))
        return self

    def to_string(self) -> str:
        """
        Assembles query into a RQL expression, multiple Q objects will be interpreted as an "AND" expression`s
        components
        :return:
        """
        # queries
        query_string = self._q_objects[0].to_string()
        for q_object in self._q_objects[1:]:
            query_string = '{}({}, {})'.format(
                'and', query_string, q_object.to_string()
            )
        # ordering options
        if self._orderings:
            ordering_expression = 'sort({})'.format(', '.join(self._orderings))
            query_string = ', '.join([query_string, ordering_expression])
        # limit option
        if self._limit:
            limit_expression = 'limit({}, {})'.format(self._limit[0], self._limit[1])
            query_string = ', '.join([query_string, limit_expression])
        return query_string

    @mark_as_unevaluated
    def order_by(self, *orderings: str):
        """
        Sets ordering to the Query object.
        Examples:
        query.order_by('person__last_name')
        query.order_by('-person__last_name') #descending ordering
        :param ordering:
        :return:
        """
        for ordering in orderings:
            ordering = ordering.replace('__', '.')
            if not ordering.startswith('-'):
                ordering = '+' + ordering
            self._orderings.append(ordering)
        return self

    @mark_as_unevaluated
    def __getitem__(self, item):
        if self._limit:
            raise Exception('Cannot limit already limited query')
        if isinstance(item, slice):
            offset = item.start
            limit = item.stop - item.start
        else:
            offset = item
            limit = 1
        self._limit = (offset, limit)
        return self

    @evaluate
    def __iter__(self):
        return self._result.__iter__()

    @evaluate
    def __len__(self):
        return self._result.__len__()

    def _evaluate(self):
        """
        Evaluates the query using RecordsManager
        """
        records = self._manager._query(self._obj, self.to_string())
        self._result = records
        self._is_evaluated = True
        return self._result