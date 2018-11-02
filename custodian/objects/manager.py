from custodian.command import Command, COMMAND_METHOD
from custodian.exceptions import ObjectUpdateException, ObjectCreateException, \
    ObjectDeletionException
from custodian.objects import Object
from custodian.objects.cache import ObjectCache
from custodian.objects.factory import ObjectFactory
from custodian.objects.fields import RelatedObjectField, LINK_TYPES


class ObjectsManager:
    _base_command_name = 'meta'
    _cache_class = ObjectCache
    _cache = None

    def __init__(self, client, use_cache):
        self.client = client
        self._pending_objects = []
        self._use_cache = use_cache
        if use_cache:
            self._cache = self._cache_class()

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
                # process referenced fields` objects
                if not self.get(field.obj.name):
                    self.create(field.obj)
                else:
                    self.update(field.obj)

            # unmark current object as pending
            self._pending_objects.remove(obj.name)
            if fields_to_add_later:
                # now update object with the rest of fields
                obj = self.update(obj)
            self._post_process_reverse_relations(obj)

            self._cache.flush()
            # retrieve final object version
            return self.get(obj.name)
        else:
            raise ObjectCreateException(data.get('msg'))

    def update(self, obj: Object) -> Object:
        """
        Updates existing object in Custodian
        :param obj:
        :return:
        """
        self._pre_process_reverse_relations(obj)
        data, ok = self.client.execute(
            command=Command(name=self._get_object_command_name(obj.name), method=COMMAND_METHOD.POST),
            data=obj.serialize()
        )
        if ok:
            self._cache.flush()
            return obj
        else:
            raise ObjectUpdateException(data.get('Msg'))

    def delete(self, obj: Object) -> Object:
        """
        Deletes existing object from Custodian
        :param obj:
        :return:
        """

        data, ok = self.client.execute(
            command=Command(name=self._get_object_command_name(obj.name), method=COMMAND_METHOD.DELETE)
        )
        if ok:
            if self._use_cache:
                self._cache.flush()
            return obj
        else:
            raise ObjectDeletionException(data.get('msg'))

    def get(self, object_name):
        """
        Retrieves existing object from Custodian by name
        :param object_name:
        """
        if not self._use_cache or self._cache.get(object_name) is None:
            data, ok = self.client.execute(
                command=Command(name=self._get_object_command_name(object_name), method=COMMAND_METHOD.GET)
            )
            obj = ObjectFactory.factory(data, objects_manager=self) if ok else None
            if ok and self._use_cache:
                self._cache.set(object_name, obj)
        if self._use_cache:
            return self._cache.get(object_name)
        else:
            return obj

    def get_all(self):
        """
        Retrieves a list of existing objects from Custodian
        :return:
        """
        data, ok = self.client.execute(
            command=Command(name=self._get_object_command_name(''), method=COMMAND_METHOD.GET)
        )
        if ok and data:
            return [ObjectFactory.factory(object_data, self) for object_data in data]
        else:
            return []

    @classmethod
    def _get_object_command_name(cls, object_name: str):
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
                # or if referenced object is not actual
                if not self.get(field.obj.name) or field.outer_link_field not in self.get(field.obj.name).fields:
                    fields_to_add_later.append(field)
                    continue
            safe_fields.append(field)
        return Object(name=obj.name, cas=obj.cas, objects_manager=self, key=obj.key, fields=safe_fields,
                      actions=obj.actions), fields_to_add_later

    def _post_process_reverse_relations(self, obj: Object):
        """
        Check if inner relation field has no corresponding outer relation field and create it if needed
        :param obj:
        """
        # check added fields
        for field in obj.fields.values():
            if isinstance(field, RelatedObjectField) and field.link_type == LINK_TYPES.INNER:
                if field.reverse_field and field.reverse_field.name not in field.obj.fields:
                    field.obj.fields[field.reverse_field.name] = field.reverse_field
                    self.update(field.obj)

    def _pre_process_reverse_relations(self, obj: Object):
        """
        Check if inner relation field has corresponding outer relation field and remove it if needed
        :param obj:
        """
        actual_object = self.get(obj.name)

        # check fields which are to remove
        for field in actual_object.fields.values():
            if isinstance(field, RelatedObjectField) and field.link_type == LINK_TYPES.INNER:
                if field.reverse_field and field.name not in obj.fields:
                    del field.obj.fields[field.reverse_field.name]
                    self.update(field.obj)

        # check field which are to add

        # it is necessary to check that related fields reference existing Custodian objects
        # if related object does not exist we need to create it first
        for field in obj.fields.values():
            if isinstance(field, RelatedObjectField) and field.link_type == LINK_TYPES.OUTER:
                if not self.get(field.obj.name):
                    self.create(field.obj)
