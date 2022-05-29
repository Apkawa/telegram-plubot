from typing import Optional

from redis.client import StrictRedis
from redis_dict import RedisDict

from plubot.builtin_plugins.storage import StorageBackendBase
from plubot.config import config


class NestedRedisDict(RedisDict):
    _parent: Optional[str]
    _redis: None

    def __init__(self, **kwargs):
        self.temp_redis = None
        # Todo validate namespace
        self.namespace = kwargs.pop('namespace', '')
        self.expire = kwargs.pop('expire', None)

        self.redis = kwargs.pop('redis', None)
        if not self.redis:
            self.redis = StrictRedis(decode_responses=True, **kwargs)
        self.get_redis = self.redis
        self.iter = self.iterkeys()


class RedisBackend(StorageBackendBase):
    store_cls = NestedRedisDict

    def _get_store(self):
        store_kw = config.get('storage_backend_config', {})
        return self.store_cls(**store_kw)

    def sub_store(self, namespace):
        return NestedRedisDict(namespace=namespace, redis=self._store.redis)


def test_backend():
    config.set('storage_backend_config', {'port': 16379})
    b = RedisBackend()
    assert 'key' not in b
    b['foo'] = 1
    assert b['foo'] == 1
    extra = b.sub_store('bar')
    extra['baz'] = 123
    extra['dict'] = {'foo': 1, 'bar': {'key': '134'}}
    assert isinstance(extra, NestedRedisDict)
    extra = b.sub_store('bar')
    assert extra['baz']
    assert extra['dict']
