import json
import re

from ._base import BaseSiteHandler, VideoLinkResultType


class VkHandler(BaseSiteHandler):
    domain = 'vk.com'

    def get_video(self, link: str) -> VideoLinkResultType:
        response = self.fetch_link(link)
        page_html = response.text
        data = re.findall(r"^\s*ajax.preload\('al_video.php',\s*(.*)\);\s*$", page_html,
                          re.MULTILINE)
        if data:
            urls = re.findall(r'"url(\d+)":\s*(".+?"),', data[0], re.MULTILINE)
            video_url_map = {}
            for s, url in urls:
                video_url_map[int(s)] = json.loads(url)
            # TODO Need download mp4
            return video_url_map[min(video_url_map)] + '&ext=.mp4'
        return None


def test_handler():
    h = VkHandler()
    links = h.get_video("https://vk.com/video-174068266_456239341")
    assert links
