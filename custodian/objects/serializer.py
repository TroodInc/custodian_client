from custodian.objects import FieldsManager, Object
from custodian.objects.fields import RelatedObjectField


class ObjectSerializer:
    @classmethod
    def deserialize(cls, object_data, object_manager):
        """
        Assembles object with provided data
        :param object_data:
        :param object_manager:
        :return:
        """
        fields = []
        for field_data in object_data['fields']:
            if field_data.get('linkMeta'):
                field_data['obj'] = object_manager.get(field_data['linkMeta'])
                field_data['type'] = RelatedObjectField.type
                field_data['link_type'] = field_data.get('linkType')
                del field_data['linkMeta']
                del field_data['linkType']
            fields.append(FieldsManager.get_field_by_type(field_data['type'])(**field_data))
        object_data['fields'] = fields
        return Object(**object_data)
