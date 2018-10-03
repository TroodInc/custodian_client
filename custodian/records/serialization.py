class RecordDataSerializer:
    @classmethod
    def serialize(cls, obj, data):
        raw_data = {}
        for field_name, value in data.items():
            raw_value = obj.fields[field_name].to_raw(value)
            if raw_value is not None:
                raw_data[field_name] = raw_value
        return raw_data
