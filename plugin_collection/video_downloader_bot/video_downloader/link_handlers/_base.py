import urllib.parse
from typing import Union, Optional, List

from requests_html import HTMLSession, HTMLResponse
from telegram.utils.types import FileInput

USER_AGENT = ("Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) "
              "Gecko/20100101 Firefox/100.0")

VideoLinkResultType = Optional[Union[FileInput, List[FileInput]]]


class BaseSiteHandler:
    domain: str = ''

    def parse_link(self, link: str) -> urllib.parse.ParseResult:
        return urllib.parse.urlparse(link)

    def fetch_link(self, link: str) -> HTMLResponse:
        session = HTMLSession()
        response = session.get(link, headers={
            "User-Agent": USER_AGENT
        })
        return response

    def is_valid(self, link: str) -> bool:
        return self.parse_link(link).hostname == self.domain

    def get_video(self, link: str) -> VideoLinkResultType:
        raise NotImplementedError("get_video not implemented")
