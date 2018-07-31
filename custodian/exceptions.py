class CommandExecutionFailureException(Exception):
    pass


class RecordAlreadyExistsException(CommandExecutionFailureException):
    pass


class ObjectUpdateException(CommandExecutionFailureException):
    pass


class ObjectCreateException(CommandExecutionFailureException):
    pass


class ObjectDeletionException(CommandExecutionFailureException):
    pass


class FieldDoesNotExistException(Exception):
    pass


class QueryException(Exception):
    pass


class ImproperlyConfiguredFieldException(Exception):
    pass


class FieldValidationException(Exception):
    pass


class RecordUpdateException(Exception):
    pass


class CasFailureException(RecordUpdateException):
    pass
