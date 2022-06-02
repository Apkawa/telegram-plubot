import os

from . import video_downloader

PLUGINS = [
    video_downloader
]

STORAGE_BACKEND = 'plubot.builtin_plugins.storage.backends.redis_backend.RedisBackend'
STORAGE_BACKEND_CONFIG = {
    'port': 16379
}
