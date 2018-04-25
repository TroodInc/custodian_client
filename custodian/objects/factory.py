from custodian.objects import FieldsManager, Object
from custodian.objects.fields import RelatedObjectField


class ObjectFactory:
    @classmethod
    def _factory_field(cls, field_data, objects_manager):
        if field_data.get('linkMeta'):
            field_data['obj'] = Object(name=field_data['linkMeta'], cas=False, objects_manager=objects_manager)
            field_data['type'] = RelatedObjectField.type
            field_data['link_type'] = field_data.get('linkType')
            field_data['outer_link_field'] = field_data.get('outerLinkField')
            del field_data['linkMeta']
            del field_data['linkType']
            if field_data.get('outerLinkField'):
                del field_data['outerLinkField']

        return FieldsManager.get_field_by_type(field_data['type'])(**field_data)

    @classmethod
    def factory(cls, object_data, objects_manager):
        """
        Assembles object with provided data
        :param object_data:
        :return:
        """
        fields = []
        for field_data in object_data['fields']:
            fields.append(cls._factory_field(field_data, objects_manager))
        object_data['fields'] = fields
        object_data['objects_manager'] = objects_manager
        return Object(**object_data)
