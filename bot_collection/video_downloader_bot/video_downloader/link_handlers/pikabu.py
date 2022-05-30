import os.path

from ._base import BaseSiteHandler, VideoLinkResultType


class PikabuHandler(BaseSiteHandler):
    domain = 'pikabu.ru'

    def get_video(self, link: str) -> VideoLinkResultType:
        response = self.fetch_link(link)
        video_els = response.html.find('.page-story__story .story .player')
        links = []
        for v_el in video_els:
            s = v_el.attrs['data-source']
            if s.endswith('.gif'):
                s = os.path.splitext(s)[0]
            links.append(s + '.mp4')
        return links


def test_handler():
    h = PikabuHandler()
    h.get_video("https://pikabu.ru/story/pravitelstvo_tibeta_v_izgnanii_9145490")
