"""
curl 'https://www.tiktok.com/@strong_love/video/7071984494680493314' \
  -H 'authority: www.tiktok.com' \
  -H 'sec-ch-ua: " Not A;Brand";v="99", "Chromium";v="99", "Google Chrome";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'upgrade-insecure-requests: 1' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' \
  -H 'sec-fetch-site: none' \
  -H 'sec-fetch-mode: navigate' \
  -H 'sec-fetch-user: ?1' \
  -H 'sec-fetch-dest: document' \
  -H 'accept-language: en-US,en;q=0.9' \
  --compressed
"""

import json
import re

from ._base import BaseSiteHandler, VideoLinkResultType


class TiktokHandler(BaseSiteHandler):
    domain = 'www.tiktok.com'

    def get_video(self, link: str) -> VideoLinkResultType:
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "en-US,en;q=0.9",
            "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"99\", \"Google Chrome\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Linux\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
        }
        response = self.fetch_link(link, req_kw={'headers': headers})
        page_html = response.text
        data = re.findall(r'"downloadAddr":\s*(".+?")', page_html, re.MULTILINE)
        if data:
            url = json.loads(data[0])
            return url + '&ext=.mp4'
        return None


def test_handler():
    h = TiktokHandler()
    links = h.get_video("https://www.tiktok.com/@strong_love/video/7071984494680493314")
    assert links
