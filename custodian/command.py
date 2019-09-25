class COMMAND_METHOD:
    DELETE = 'delete'
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    PATCH = 'patch'

    @classmethod
    def get_available_methods(cls):
        return [value for key, value in cls.__dict__.items() if not key.startswith('__') and isinstance(value, str)]


class Command:
    name: str
    method: str

    def __init__(self, name: str, method: str):
        assert method in COMMAND_METHOD.get_available_methods(), 'Method must be one of the COMMAND_METHOD`s attribute'
        self.name = name
        self.method = method

    def __repr__(self):
        return '<Command name="{}" method="{}">'.format(self.name, self.method)
