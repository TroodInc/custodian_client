class CommandExecutionFailureException(Exception):
    pass


class FieldDoesNotExistException(Exception):
    pass


class QueryException(Exception):
    pass


class ImproperlyConfiguredFieldException(Exception):
    pass


class RecordAlreadyExistsException(CommandExecutionFailureException):
    pass


class ObjectUpdateException(CommandExecutionFailureException):
    pass


class ObjectCreateException(CommandExecutionFailureException):
    pass
