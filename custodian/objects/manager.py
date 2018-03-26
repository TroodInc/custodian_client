from custodian.command import Command, COMMAND_METHOD
from custodian.exceptions import ObjectUpdateException, ObjectCreateException, \
    ObjectDeletionException
from custodian.objects import Object
from custodian.objects.fields import RelatedObjectField
from custodian.objects.serializer import ObjectSerializer


class ObjectsManager:
    _base_command_name = 'meta'

    def __init__(self, client):
        self.client = client
        self._pending_objects = []

    @classmethod
    def get_object_command_name(cls, object_name: str):
        """
        Constructs API command for existing Custodian object
        :param obj:
        :return:
        """
        return '/'.join([cls._base_command_name, object_name])

    def _split_object_by_phases(self, obj: Object):
        """
        In case of referencing non-existing object split object into "safe" object and fields to add to this object later
        :param obj:
        :return:
        """
        safe_fields = []
        fields_to_add_later = []
        for field in obj.fields.values():
            if isinstance(field, RelatedObjectField):
                # if object contains field which references the object which does not exist yet
                if not self.get(field.obj.name):
                    fields_to_add_later.append(field)
                    continue
            safe_fields.append(field)
        return Object(obj.name, obj.cas, self, obj.key, safe_fields), fields_to_add_later

    def create(self, obj: Object) -> Object:
        """
        Creates new object in Custodian
        :param obj:
        :return:
        """
        # omit if this object is already pending
        if obj.name in self._pending_objects:
            return

        safe_obj, fields_to_add_later = self._split_object_by_phases(obj)
        # mark current object as pending
        self._pending_objects.append(safe_obj.name)
        # create safe object
        data, ok = self.client.execute(
            command=Command(name=self._base_command_name, method=COMMAND_METHOD.PUT),
            data=safe_obj.serialize()
        )
        if ok:
            for field in fields_to_add_later:
                # create referenced fields
                self.create(field.obj)
            # unmark current object as pending
            self._pending_objects.remove(obj.name)
            if fields_to_add_later:
                # now update object with the rest of fields
                return self.update(obj)
            else:
                return obj
        else:
            raise ObjectCreateException(data.get('msg'))

    def update(self, obj: Object) -> Object:
        """
        Updates existing object in Custodian
        :param obj:
        :return:
        """
        # it is necessary to check that related fields reference existing Custodian objects
        # if related object does not exist we need to create it first
        for field in obj.fields.values():
            if isinstance(field, RelatedObjectField) and field.link_type == RelatedObjectField.LINK_TYPES.OUTER:
                if not self.get(field.obj.name):
                    self.create(field.obj)
        data, ok = self.client.execute(
            command=Command(name=self.get_object_command_name(obj.name), method=COMMAND_METHOD.POST),
            data=obj.serialize()
        )
        if ok:
            return obj
        else:
            raise ObjectUpdateException(data.get('msg'))

    def delete(self, obj: Object) -> Object:
        """
        Deletes existing object from Custodian
        :param obj:
        :return:
        """

        data, ok = self.client.execute(
            command=Command(name=self.get_object_command_name(obj.name), method=COMMAND_METHOD.DELETE)
        )
        if ok:
            return obj
        else:
            raise ObjectDeletionException(data.get('msg'))

    def get(self, object_name):
        """
        Retrieves existing object from Custodian by name
        :param object_name:
        """
        data, ok = self.client.execute(
            command=Command(name=self.get_object_command_name(object_name), method=COMMAND_METHOD.GET)
        )
        obj = ObjectSerializer.deserialize(data, objects_manager=self) if ok else None
        return obj

    def get_all(self):
        """
        Retrieves a list of existing objects from Custodian
        :return:
        """
        data, ok = self.client.execute(
            command=Command(name=self.get_object_command_name(''), method=COMMAND_METHOD.GET)
        )
        if ok and data:
            return [ObjectSerializer.deserialize(object_data, self) for object_data in data]
        else:
            return []
