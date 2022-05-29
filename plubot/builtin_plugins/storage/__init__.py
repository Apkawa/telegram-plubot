import importlib
from typing import Optional, Type, Union

from .backends.base import StorageBackendBase
from .backends.memory_backend import MemoryBackend
from ...config import config
from ...plugin import hookimpl, hook_types


def get_store_backend_class() -> Type[StorageBackendBase]:
    storage_backend = config.get('storage_backend', MemoryBackend)
    if isinstance(storage_backend, str):
        module, cls = storage_backend.rsplit('.', 1)
        m = importlib.import_module(module)
        return getattr(m, cls)
    return storage_backend


class ChatData:
    """Custom class for chat_data. Here we store data per message."""

    def __init__(self, store: Optional[StorageBackendBase] = None) -> None:
        super().__init__()
        self.__store = store or get_store_backend_class()()

    @property
    def store(self):
        return self.__store


@hookimpl
def bot_data_class() -> hook_types.HookChatDataClassReturnType:
    return ChatData


@hookimpl
def chat_data_class() -> hook_types.HookChatDataClassReturnType:
    return ChatData

@hookimpl
def user_data_class() -> hook_types.HookChatDataClassReturnType:
    return ChatData
