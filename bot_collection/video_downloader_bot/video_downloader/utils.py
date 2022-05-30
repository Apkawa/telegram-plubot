import re
from typing import List


def extract_links(text: str) -> List[str]:
    """
    >>> extract_links('https://example.ru/video.mp4')
    ['https://example.ru/video.mp4']
    >>> extract_links('Foo https://example.ru/video.mp4 bar https://example.ru/video_2.mp4 baz')
    ['https://example.ru/video.mp4', 'https://example.ru/video_2.mp4']

    """
    return re.findall(r'(https?://\S+)', text)
