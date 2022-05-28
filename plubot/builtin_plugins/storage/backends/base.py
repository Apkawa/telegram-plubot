

class StorageBackendBase:
    __not_given = object()

    store_cls = dict

    def __init__(self):
        self._store = self.store_cls()

    def __contains__(self, key):
        return key in self._store

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        del self._store[key]

    def get(self, key, default=None):
        return self._store.get(key, default)

    def pop(self, key, default=__not_given):
        args = () if default is self.__not_given else (default,)
        return self._store.pop(key, *args)

    def setdefault(self, key, value):
        if key in self._store:
            return self._store[key]
        else:
            self._store[key] = value
            return value

    def update(self, dict_):
        self._store.update(dict_)

    def has_key(self, key):
        return key in self._store

    def keys(self):
        return self._store.keys()

    def values(self):
        return self._store.values()

    def items(self):
        return self._store.items()

    def iterkeys(self):
        return self._store.iterkeys()

    def itervalues(self):
        return self._store.itervalues()

    def iteritems(self):
        return self._store.iteritems()

    def clear(self):
        # To avoid unnecessary persistent storage accesses, we set up the
        # internals directly (loading data wastes time, since we are going to
        # set it to an empty dict anyway).
        self._store = {}

