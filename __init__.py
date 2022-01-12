from urllib.parse import urljoin

import requests
import requests.exceptions as rex

from .anime import Anime
from .manga import Manga
from .utils.download import download

class NoContentError(Exception):
    """Error for objects with no data."""
    pass


class MALError(Exception):
    """All catch all error for MyAnimeList."""
    pass


class MyAnimeList:
    """This is a class for accessing data from myanimelist.net.
    
    Attributes
    ----------
        base_url (str): The base url for navigating myanimelist.net.
        session (requests.Session): The session used for requests.
        rate_limit (int/float): The time to wait after each request.
    """
    __slots__ = ("base_url", "session", "rate_limit")

    def __init__(self, session=None) -> None:
        """
        The constructor of the MyAnimeList class.
        
        Parameters
        ----------
            session (requets.Session) (optional): The session used for requests.
        """
        self.base_url = "https://myanimelist.net"
        self.session = session if session else requests.session()
        self.rate_limit = 4.05
    
    def get_anime(self, id:int) -> Anime:
        """Given an id, return an Anime object using data
        from MyAnimeList.
        
        Parameters
        ----------
            id: An int or int-equivalent object that represents an
                anime from MyAnimeList.

        Returns
        -------
            Anime: An Anime object containing metadata for anime that the
                given id parameters represents.
        """
        # Do not allow non-number values for id.
        if not isinstance(eval(id), int): raise MALError

        req = download(f"{self.base_url}/anime/{id}", driver=self.session, wait_time=self.rate_limit)

        if req.ok:
            return Anime(req)
        elif req.status_code == 404:
            raise NoContentError
        else:
            raise MALError

    def get_manga(self, id:int) -> Manga:
        """Given an id, return a Manga object using data
        from MyAnimeList.
        
        Parameters
        ----------
            id: An int or int-equivalent object that represents a
                manga from MyAnimeList.

        Returns
        -------
            Manga: A Manga object containing metadata for manga that the
                given id parameters represents.
        """
        req = download(
            f"{self.base_url}/manga/{id}",
            driver=self.session, wait_time=self.rate_limit
        )

        if req.ok:
            return Manga(req)
        elif req.status_code == 404:
            raise NoContentError
        else:
            raise MALError
    
    def validate_url(self, url:str) -> bool:
        """Tests the connection to the given url"""
        try:
            self.session.head(url).raise_for_status()
            return True
        except (rex.MissingSchema, rex.HTTPError):
            return False