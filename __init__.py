from urllib.parse import urljoin

import requests
import requests.exceptions as rex

from .anime import Anime
from .manga import Manga
from .utils.download import download


class NoContentError(Exception):
    pass


class MALError(Exception):
    """All catch all error for MyAnimeList"""
    pass


class MyAnimeList:
    __slots__ = ("base_url", "session", "rate_limit")

    def __init__(self, session=None) -> None:
        self.base_url = "https://myanimelist.net"
        self.session = session if session else requests.session()
        self.rate_limit = 4.05
    
    def get_anime(self, id) -> Anime:
        req = download(f"{self.base_url}/anime/{id}", driver=self.session, wait_time=self.rate_limit)

        if req.ok:
            return Anime(req)
        elif req.status_code == 404:
            raise NoContentError
        else:
            raise MALError

    def get_manga(self, id) -> Manga:
        req = download(f"{self.base_url}/manga/{id}", driver=self.session, wait_time=self.rate_limit)

        if req.ok:
            return Manga(req)
        elif req.status_code == 404:
            raise NoContentError
        else:
            raise MALError
    
    def validate_url(self, url) -> bool:
        """
        Sends a test packet to url and returns True if
        the connection is good. Returns False otherwise.
        """
        try:
            self.session.head(url).raise_for_status()
            return True
        except (rex.MissingSchema, rex.HTTPError):
            return False