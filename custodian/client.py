import requests

from custodian.command import Command
from custodian.exceptions import CommandExecutionFailureException
from custodian.objects.manager import ObjectsManager
from custodian.records.manager import RecordsManager


class Client:
    _records_manager_class = RecordsManager
    _objects_manager_class = ObjectsManager

    server_url = None

    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip('/')
        self.records = self._records_manager_class(self)
        self.objects = self._objects_manager_class(self)

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
        response = getattr(requests, command.method)(url, json=data, params=params)
        response_content = response.json()
        if response_content['status'] == 'OK':
            return response_content.get('data', None)
        else:
            raise CommandExecutionFailureException('Command execution failed')
