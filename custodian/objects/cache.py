from custodian.objects import Object


class ObjectCache:
    # TODO: implement cache invalidation
    _objects_map_cache = {}

    def __init__(self):
        self._objects_map_cache = {}

    def get(self, object_name: str):
        return self._objects_map_cache.get(object_name, None)

    def set(self, object_name: str, obj: Object):
        self._objects_map_cache[object_name] = obj

    def flush(self):
        self._objects_map_cache = {}
