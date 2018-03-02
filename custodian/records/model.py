from custodian.exceptions import FieldValidationException
from custodian.objects import Object


class Record:
    obj = None

    def __init__(self, obj: Object, **values):
        """
        Assembles a record based on obj.fields specification
        :param obj:
        :param values:
        """
        self.obj = obj
        for field in obj.fields.values():
            value = values.get(field.name, None)
            # convert value if it is set
            if value:
                value = field.from_raw(value)
            setattr(self, field.name, value)

    def _validate_values(self):
        """
        Check record`s values
        """
        for field_name, field in self.obj.fields.items():
            if not field.optional and getattr(self, field.name) is None:
                raise FieldValidationException('Null value in "{}" violates not-null constraint'.format(field_name))

    def serialize(self):
        """
        Serialize record values, empty values are skipped
        :return:
        """
        self._validate_values()
        data = {}
        for field_name, field in self.obj.fields.items():
            raw_value = field.to_raw(getattr(self, field.name))
            if raw_value is not None:
                data[field.name] = raw_value
        return data

    def __repr__(self):
        return '<Record #{} of "{}" object>'.format(self.get_pk(), self.obj.name)

    def get_pk(self):
        """
        Returns the record`s primary key value
        """
        return getattr(self, self.obj.key)

    def exists(self):
        """
        True if the record exists in the Custodian
        :return:
        """
        # TODO: add check via API call
        return self.get_pk() is not None