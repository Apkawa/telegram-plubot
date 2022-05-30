import os.path
from collections import namedtuple
from typing import List, Optional, NamedTuple, Type

from telegram.utils.types import FileInput

from .link_handlers import get_video_from_link


class VideoLinkResult(NamedTuple):
    url: str
    name: str
    video: FileInput


def extract_video_from_links(links: List[str]) -> List[Optional[VideoLinkResult]]:
    for link in links:
        video_links = get_video_from_link(link)
        if not video_links:
            continue
        if not isinstance(video_links, list):
            video_links = [video_links]
        for video_link in video_links:
            name = os.path.split(link.split('?')[0])[-1]
            yield VideoLinkResult(link, name, video_link)
