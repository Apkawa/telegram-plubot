from typing import List, Optional

from telegram.utils.types import FileInput

from .link_handlers import get_video_from_link


def extract_video_from_links(links: List[str]) -> List[Optional[FileInput]]:
    for link in links:
        video_links = get_video_from_link(link)
        if not video_links:
            continue
        if not isinstance(video_links, list):
            video_links = [video_links]
        for video_link in video_links:
            yield video_link
