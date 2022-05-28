from typing import Optional

from .backends.base import StorageBackendBase
from .backends.memory import MemoryBackend
from ...plugin import hookimpl, hook_types


class ChatData:
    """Custom class for chat_data. Here we store data per message."""

    def __init__(self, store: Optional[StorageBackendBase] = None) -> None:
        super().__init__()
        self.__store = store or MemoryBackend()

    @property
    def store(self):
        return self.__store


@hookimpl
def chat_data_class() -> hook_types.HookChatDataClassReturnType:
    return ChatData
