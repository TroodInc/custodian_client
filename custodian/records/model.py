from custodian.objects.model import Object


class Record:
    obj = None

    def __init__(self, obj: Object, **kwargs):
        """
        Assembles record based on obj.fields specification
        :param obj:
        :param kwargs:
        """
        self.obj = obj
        for field in obj.fields:
            value = kwargs.get(field.name, None)
            if value is None:
                if field.optional:
                    value = field.get_default_value()
                else:
                    raise ValueError('"{}" field is required'.format(field.name))
            setattr(self, field.name, value)

    def serialize(self):
        data = {}
        for field in self.obj.fields:
            data[field.name] = field.to_raw(getattr(self, field.name))
        return data

    def __repr__(self):
        return '<Record #{} of "{}" object>'.format(getattr(self, self.obj.key), self.obj.name)
