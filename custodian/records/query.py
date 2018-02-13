from copy import deepcopy

from custodian.objects.model import Object


class Q:
    _query = None
    _logical_expressions = None
    _inverted = None

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
        return operator, field


class Query:
    _q_objects = None

    def __init__(self, obj: Object):
        self.obj = obj
        self._q_objects = []

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
        query_string = self._q_objects[0].to_string()
        for q_object in self._q_objects[1:]:
            query_string = '{}({}, {})'.format(
                'and', query_string, q_object.to_string()
            )
        return query_string
