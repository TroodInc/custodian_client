from custodian.objects.fields import RelatedObjectField, LINK_TYPES, GenericField, ObjectsField


class RecordDataSerializer:
    @classmethod
    def _serialize_simple_value(cls, field, value):
        return field.to_raw(value)

    @classmethod
    def _serialize_inner_link_data(cls, field, value):
        from custodian.records.model import Record
        assert field.link_type == LINK_TYPES.INNER, \
            'Attempt to serialize dict value into outer field'
        if isinstance(value, Record):
            return cls.serialize(field.obj, value.data)
        else:
            return cls._serialize_simple_value(field, value)

    @classmethod
    def _serialize_generic_inner_link_data(cls, field, value):
        assert field.link_type == LINK_TYPES.INNER, \
            'Attempt to serialize dict value into outer field'
        if isinstance(value, dict) or value is None:
            return cls._serialize_simple_value(field, value)
        else:
            return {**cls.serialize(value.obj, value.data), **{'_object': value.obj.name}}

    @classmethod
    def _serialize_inner_objects_data(cls, field, value):
        from custodian.records.model import Record
        values = []
        for item in value:
            if isinstance(item, dict) or item is None:
                values.append(cls._serialize_simple_value(field, item))
            elif isinstance(item, Record):
                values.append(item.serialize())
            else:
                values.append(field.obj.fields[field.obj.key].to_raw(item))
        return values

    @classmethod
    def _serialize_outer_link_data(cls, field, value):
        from custodian.records.model import Record
        assert field.link_type == LINK_TYPES.OUTER, \
            'Attempt to serialize list value for inner field'
        values = []
        for item in value:
            if isinstance(item, Record):
                values.append(cls.serialize(field.obj, item.data))
            else:
                values.append(cls._serialize_simple_value(field, item))
        return values

    @classmethod
    def serialize(cls, obj, data):
        raw_data = {}
        for field_name, value in data.items():
            field = obj.fields[field_name]
            if isinstance(field, RelatedObjectField):
                if field.link_type == LINK_TYPES.INNER:
                    raw_data[field_name] = cls._serialize_inner_link_data(field, value)
                else:
                    raw_data[field_name] = cls._serialize_outer_link_data(field, value)
            elif isinstance(field, GenericField):
                if field.link_type == LINK_TYPES.INNER:
                    raw_data[field_name] = cls._serialize_generic_inner_link_data(field, value)
                else:
                    raw_data[field_name] = cls._serialize_outer_link_data(field, value)
            elif isinstance(field, ObjectsField):
                if field.link_type == LINK_TYPES.INNER:
                    raw_data[field_name] = cls._serialize_inner_objects_data(field, value)
            else:
                raw_data[field_name] = cls._serialize_simple_value(field, value)

        # PK value should be defined or not set at all
        if raw_data.get(obj.key, None) is None:
            try:
                del raw_data[obj.key]
            except KeyError:
                pass
        return raw_data
