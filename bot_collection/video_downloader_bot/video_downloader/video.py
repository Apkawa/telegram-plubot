import enum
import os.path
from collections import namedtuple
from hashlib import sha1
from pathlib import Path
from typing import List, Optional, NamedTuple, Type, Union, Dict
from unittest import mock

from telegram import Video
from telegram.utils.types import FileInput

from . import Converter
from .link_handlers import get_video_from_link
from .utils import CleanablePath

VideoType = Union[Video, FileInput]


class VideoLinkResult(NamedTuple):
    url: str
    name: str
    video: VideoType


def map_video_result(link: str, video_links: List[VideoType]):
    video_links = video_links or []
    if not isinstance(video_links, list):
        video_links = [video_links]
    for video_link in video_links:
        path = link
        if isinstance(video_link, str):
            path = video_link
        name = os.path.split(path.split('?')[0])[-1]
        yield VideoLinkResult(link, name, video_link)


def extract_video(link: str) -> List[VideoLinkResult]:
    video_links = get_video_from_link(link)
    return list(map_video_result(link, video_links))


class ProcessState(enum.Enum):
    DOWNLOAD = 'download'
    CONVERT = 'convert'
    READY = 'ready'
    ERROR = 'error'
    END = 'end'


class ProcessResult:
    state: ProcessState
    result: Optional[VideoLinkResult]
    error: Optional[Exception]

    def __init__(self,
                 state: ProcessState,
                 result: Optional[VideoLinkResult] = None,
                 error: Optional[Exception] = None
                 ):
        self.state = state
        self.result = result
        self.error = error

    def __str__(self):
        return self.state


def process_link(raw_link: str, cache: Dict[str, List[dict]]):
    link_hash = sha1(raw_link.encode("utf-8")).hexdigest()
    cache_key = link_hash
    video_links = cache.get(link_hash)
    if video_links:
        video_links = map_video_result(raw_link, [
            Video(**v) for v in video_links if 'duration' in v])

    if not video_links:
        video_links = extract_video(raw_link)

    cached_video = []
    conv = Converter(workdir='/tmp/')

    def _generator(video_result: VideoLinkResult):
        link = video_result.video
        if not link:
            return
        yield ProcessResult(ProcessState.DOWNLOAD)
        if isinstance(link, str):
            # Other links must be already converted
            ext = os.path.splitext(link)[-1]

            if ext in ['.webm']:
                yield ProcessResult(ProcessState.CONVERT)
                try:
                    filepath = CleanablePath(conv.fetch(link))
                    mp4_filepath = CleanablePath(conv.to_mp4(filepath))
                except Exception as e:
                    yield ProcessResult(ProcessState.ERROR, error=e)
                    return
                link = open(mp4_filepath, 'rb')
                video_result = VideoLinkResult(
                    url=video_result.url,
                    name=video_result.name + '.mp4',
                    video=link
                )
        video_file = yield ProcessResult(ProcessState.READY, video_result)
        if video_file:
            cached_video.append(video_file.to_dict())

        yield ProcessResult(ProcessState.END)

    for video_result in video_links:
        yield _generator(video_result)

    cache[cache_key] = cached_video


def test_process_link():
    cache = {}
    gen = process_link("http://example.com/video.mp4", cache)
    states = []
    for v_gen in gen:
        for g in v_gen:
            states.append(g.state)
            if g.state == ProcessState.READY:
                v_gen.send(mock.Mock())
    assert cache.keys()
    assert states == [ProcessState.DOWNLOAD, ProcessState.READY]


def test_process_fake_webm():
    cache = {}
    gen = process_link("http://example.com/video.webm", cache)
    states = []
    for v_gen in gen:
        for g in v_gen:
            states.append(g.state)
            if g.state == ProcessState.READY:
                v_gen.send(mock.Mock())
    assert cache.keys()
    assert states == [
        ProcessState.DOWNLOAD,
        ProcessState.CONVERT,
        ProcessState.ERROR,
    ]


def test_process_webm():
    cache = {}
    gen = process_link("https://cs14.pikabu.ru/post_img/2022/05/28/8/1653742195136846338.webm",
                       cache)
    states = []
    res = None
    for v_gen in gen:
        for g in v_gen:
            states.append(g.state)
            if g.state == ProcessState.READY:
                res = g.result
                # Must be store or use this file before cycle exit
                v = Path(res.video.name)
                assert v.exists()
                v_gen.send(mock.Mock())
    assert res
    # Already cleanup temp files
    v = Path(res.video.name)
    assert not v.exists()

    assert cache.keys()
    assert states == [
        ProcessState.DOWNLOAD,
        ProcessState.CONVERT,
        ProcessState.READY,
    ]


def test_process_link_with_multiple_videos():
    cache = {}
    gen = process_link("https://pikabu.ru/story/pestraya_podborka_gifok_s_sobakami_9153441", cache)
    states = []
    for v_gen in gen:
        for g in v_gen:
            states.append(g.state)
            if g.state == ProcessState.READY:
                v_gen.send(mock.Mock())
    assert cache.keys()
    assert states == [ProcessState.DOWNLOAD, ProcessState.READY] * 6
