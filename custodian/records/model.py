from custodian.objects.model import Object


class Record:
    obj = None

    def __init__(self, obj: Object, **kwargs):
        """
        Assembles a record based on obj.fields specification
        :param obj:
        :param kwargs:
        """
        self.obj = obj
        for field in obj.fields:
            value = kwargs.get(field.name, None)
            setattr(self, field.name, value)

    def serialize(self):
        data = {}
        for field in self.obj.fields:
            data[field.name] = field.to_raw(getattr(self, field.name))
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
