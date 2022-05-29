import os.path
from typing import List, TYPE_CHECKING, Type, Optional

if TYPE_CHECKING:
    from ._base import BaseSiteHandler, VideoLinkResultType

from telegram.utils.types import FileInput


def get_handlers() -> List['BaseSiteHandler']:
    from .pikabu import PikabuHandler

    handler_classes = [
        PikabuHandler
    ]

    return [h() for h in handler_classes]


def get_video_from_link(link: str) -> Optional['VideoLinkResultType']:
    ext = os.path.splitext(link)[-1]
    if ext in ['.mp4', '.webm', '.gif']:
        return link
    for h in get_handlers():
        if h.is_valid(link):
            return h.get_video(link)