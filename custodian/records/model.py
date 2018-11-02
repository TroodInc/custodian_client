from custodian.objects import Object
from custodian.records.factory import RecordFactory
from custodian.records.serialization import RecordDataSerializer
from custodian.records.validation import RecordValidator


class Record:
    obj = None
    _validation_class = RecordValidator
    _serialization_class = RecordDataSerializer
    _factory_class = RecordFactory
    __data = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not kwargs.pop('_factory_mode', False):
            args = args[1:]
            return cls._factory_class.factory(*args, **kwargs)
        else:
            return super(Record, cls).__new__(args[0])

    def __init__(self, obj: Object, **values):
        try:
            del values['_factory_mode']
        except KeyError:
            pass
        if self.__data is None:
            self.__data = {}
        if self.obj is None:
            self.obj = obj

    def __setattr__(self, key, value):
        if key in self.__class__.__dict__:
            super(Record, self).__setattr__(key, value)
        else:
            self.__data[key] = value

    def __getattr__(self, item):
        return self.__data[item]

    @property
    def data(self):
        return self.__data

    def serialize(self):
        """
        Serialize record values, empty values are skipped
        :return:
        """
        self._validation_class.validate_full(self.obj, self.__data)
        return self._serialization_class.serialize(self.obj, self.__data)

    def __repr__(self):
        return '<Record #{} of "{}" object>'.format(self.get_pk(), self.obj.name)

    def get_pk(self):
        """
        Returns the record`s primary key value
        """
        return getattr(self, self.obj.key, None)

    def exists(self):
        """
        True if the record exists in the Custodian
        :return:
        """
        # TODO: add check via API call
        return self.get_pk() is not None
