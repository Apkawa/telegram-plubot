"""
curl https://vxtwitter.com/merci_bo/status/1530949541901500416 -H "User-Agent: TelegramBot (like TwitterBot)"
"""
import os.path

from ._base import BaseSiteHandler, VideoLinkResultType


class TwitterHandler(BaseSiteHandler):
    domain = 'pikabu.ru'

    def is_valid(self, link: str) -> bool:
        host = self.parse_link(link).hostname
        return host in ['nitter.net', 'twitter.com', 'vxtwitter.com']

    def get_video(self, link: str) -> VideoLinkResultType:
        path = self.parse_link(link).path
        new_link = "https://vxtwitter.com" + path
        response = self.fetch_link(new_link, req_kw=dict(
            headers={'User-Agent': 'TelegramBot (like TwitterBot)'}))
        video_els = response.html.find("meta[property='og:url']")
        if video_els:
            return video_els[0].attrs['content'].split("?")[0]
        return None
