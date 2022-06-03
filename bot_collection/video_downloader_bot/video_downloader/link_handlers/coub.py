"""
curl https://vxtwitter.com/merci_bo/status/1530949541901500416 -H "User-Agent: TelegramBot (like TwitterBot)"
"""
import json

from ._base import BaseSiteHandler, VideoLinkResultType


class CoubHandler(BaseSiteHandler):
    domain = 'coub.com'

    def get_video(self, link: str) -> VideoLinkResultType:
        response = self.fetch_link(link, req_kw=dict(
            headers={'User-Agent': 'TelegramBot (like TwitterBot)'}))
        video_els = response.html.find("#coubPageCoubJson")
        if video_els:
            data = json.loads(video_els[0].text)
            return data['file_versions']['share']['default']
        return None


def test_coub_handler():
    h = CoubHandler()
    links = h.get_video("https://coub.com/view/32v2av")
    assert links
