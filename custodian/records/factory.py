from custodian.objects.fields import RelatedObjectField, GenericField, LINK_TYPES


class RecordFactory:
    @classmethod
    def _factory_simple_value(cls, field, value):
        return field.from_raw(value)

    @classmethod
    def _factory_inner_link(cls, field, value):
        assert field.link_type == LINK_TYPES.INNER, \
            'Attempt to serialize dict value into outer field'
        return cls.factory(field.obj, **value)

    @classmethod
    def _factory_generic_inner_link(cls, field, value):
        assert field.link_type == LINK_TYPES.INNER, \
            'Attempt to serialize dict value into outer field'
        obj = {x.name: x for x in field.objs}[value['_object']]
        if '_object' in value and obj.key in value and len(value.keys()) == 2:
            return cls._factory_simple_value(field, value)
        else:
            return cls.factory(obj, **value)

    @classmethod
    def _factory_outer_link_data(cls, field, value):
        assert field.link_type == LINK_TYPES.OUTER, \
            'Attempt to serialize list value for inner field'
        values = []
        for item in value:
            if isinstance(item, dict):
                values.append(cls.factory(field.obj, **item))
            else:
                values.append(cls._factory_simple_value(field.obj.fields[field.obj.key], item))
        return values

    @classmethod
    def factory(cls, obj, **raw_data):
        from custodian.records.model import Record
        values = {}
        for field_name, value in raw_data.items():
            if field_name in obj.fields:
                field = obj.fields[field_name]
                if isinstance(value, dict):
                    if isinstance(field, RelatedObjectField):
                        values[field_name] = cls._factory_inner_link(field, value)
                    elif isinstance(field, GenericField):
                        values[field_name] = cls._factory_generic_inner_link(field, value)
                    else:
                        assert isinstance(field, RelatedObjectField), \
                            'Attempt to deserialize dict value into non-object field'
                elif isinstance(value, list):
                    values[field_name] = cls._factory_outer_link_data(field, value)
                else:
                    values[field_name] = cls._factory_simple_value(field, value)

        record = Record(obj, _factory_mode=True)
        for key, value in values.items():
            setattr(record, key, value)
        return record
