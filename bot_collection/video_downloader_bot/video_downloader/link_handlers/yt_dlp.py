from io import BytesIO

import requests
from yt_dlp import YoutubeDL
from yt_dlp.utils import sanitized_Request

from ._base import BaseSiteHandler, VideoLinkResultType

youtube_dl = YoutubeDL()


class YtDLPHandler(BaseSiteHandler):
    domain = None

    def is_valid(self, link: str) -> bool:
        with YoutubeDL() as dl:
            for ie_key, ie in dl._ies.items():
                if not ie.suitable(link):
                    continue

                if not ie.working():
                    continue

                if ie_key == 'Generic':
                    continue
                return True
        return False

    def select_format(self, formats):
        max_width = 500  # px
        max_size = 10 * 1024 * 1024  # 10Mb
        f_formats = []
        for f in formats:
            if f['video_ext'] != 'mp4':
                continue
            if f['width'] > max_width:
                continue
            if not f['filesize'] or f['filesize'] > max_size:
                continue
            f_formats.append(f)
        return sorted(f_formats, key=lambda f: f['width'], reverse=True)[0]

    def get_video(self, link: str) -> VideoLinkResultType:
        with YoutubeDL() as dl:
            r = dl.extract_info(link, download=False)
            f = self.select_format(r['formats'])
            uf = dl.urlopen(sanitized_Request(f['url'], headers=f.get('http_headers', {})))
            if uf.status == 200:
                return uf
            else:
                # TODO handle error
                pass
        return None


def test_handler():
    h = YtDLPHandler()
    assert h.is_valid("https://www.youtube.com/shorts/wAYJYBKoG70")
    links = h.get_video("https://www.youtube.com/shorts/wAYJYBKoG70")
    assert links
