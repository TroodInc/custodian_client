from custodian.exceptions import FieldValidationException
from custodian.objects import Object


class RecordValidator:
    @classmethod
    def validate_partial(cls, obj: Object, record_data: dict):
        """
        Check record`s
        """
        for field_name, value in record_data.items():
            if field_name not in obj.fields:
                raise FieldValidationException('Object {} does not have field {}'.format(obj.name, field_name))
            else:
                cls.__validate_value(obj.fields[field_name], value)

    @classmethod
    def validate_full(cls, obj: Object, record_data: dict):
        """
        Check record`s values
        """
        for field_name, field in obj.fields.items():
            cls.__validate_value(field, record_data.get(field_name, None))

    @classmethod
    def __validate_value(cls, field, value):
        if not field.optional and value is None:
            raise FieldValidationException('Null value in "{}" violates not-null constraint'.format(field.name))
