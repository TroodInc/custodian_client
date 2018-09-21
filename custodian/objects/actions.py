from typing import List


class Action:
    method: str = None
    protocol: str = None
    args: List[str] = None
    include_values: dict = None
    active_if_not_root: bool = None

    def __init__(self, method: str, args: List[str], protocol: str = 'REST', include_values: dict = None,
                 active_if_not_root: bool = True):
        self.method = method
        self.protocol = protocol.upper()
        self.args = args
        self.active_if_not_root = active_if_not_root
        self.include_values = include_values or {}

    def __str__(self):
        return "<Action(protocol:{}, method:{})>".format(self.protocol, self.method)

    def serialize(self):
        return {
            "method": self.method,
            "protocol": self.protocol,
            "args": self.args,
            "activeIfNotRoot": self.active_if_not_root,
            "includeValues": self.include_values
        }

    @classmethod
    def factory(cls, data):
        return cls(
            method=data['method'],
            protocol=data['protocol'],
            args=data['args'],
            active_if_not_root=data['activeIfNotRoot'],
            include_values=data['includeValues']
        )
