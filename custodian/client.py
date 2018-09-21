import json
import logging

import requests

from custodian.command import Command
from custodian.exceptions import CommandExecutionFailureException
from custodian.objects.manager import ObjectsManager
from custodian.records.manager import RecordsManager

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class Client:
    __instances = {}
    _records_manager_class = RecordsManager
    _objects_manager_class = ObjectsManager

    server_url = None
    authorization_token = None

    @classmethod
    def __new__(cls, *args, use_cache=False, **kwargs, ):
        if use_cache in kwargs:
            args_key = ''.join([x for x in args[1:]] + [x for x in kwargs.values()])
            if args_key not in cls.__instances:
                cls.__instances[args_key] = super().__new__(cls)
            return cls.__instances[args_key]
        else:
            return super().__new__(cls)

    def __init__(self, server_url: str, authorization_token: str = None, use_cache=True):
        self.server_url = server_url.rstrip('/')
        self.authorization_token = authorization_token
        self.records = self._records_manager_class(self)
        self.objects = self._objects_manager_class(self, use_cache=use_cache)

    def _make_query_string(self, params: dict):
        queries = []
        for key, value in params.items():
            queries.append('{}={}'.format(key, value))
        return '&'.join(queries)

    def execute(self, command: Command, data: dict = None, params: dict = None):
        """
        Performs call to the Custodian server API
        :param command:
        :param data:
        :param params:
        :return:
        :raises CommandExecutionFailureException:
        """
        url = '/'.join([self.server_url, command.name])
        logger.debug('Making {} request: url = "{}", json = "{}", query = "{}"'.format(
            command.method.upper(),
            url,
            json.dumps(data or {}),
            self._make_query_string(
                params or {}))
        )
        if self.authorization_token:
            headers = {'Authorization': self.authorization_token}
        else:
            headers = {}
        response = getattr(requests, command.method)(url, json=data, params=self._make_query_string(params or {}),
                                                     headers=headers)
        if response.content:
            response_content = response.json()
            if response_content['status'] == 'OK':
                return response_content.get('data', None), True
            else:
                return response_content.get('error', None), False
        else:
            if response.status_code == 204:
                return None, True
            else:
                raise CommandExecutionFailureException('Command execution failed')
