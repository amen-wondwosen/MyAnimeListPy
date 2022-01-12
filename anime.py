from collections import defaultdict
import time

import bs4
from bs4 import BeautifulSoup

from . import utils
from .utils.download import download

class Anime:
    """This is a class for gathering data scrapped from webpages
    containing seasonal from MyAnimeList anime pages.

    Attributes
    -----------
        id (int|str): A uid for representing an anime on MyAnimeList.
        title (str): The title of the anime.
        english (list): A list of english names.
        synonyms (list): A list of alternative names.
        japanese (list): A list of japanese/native names.
        type (str): The type of media (TV, Movie, OVA, etc.).
        episodes (int|str): The episode count of the anime.
        status (str): The airing status of the anime.
        aired (str): When the anime aired (start and end dates are optional).
        season (str): The season the anime aired (WINTER/SPRING/SUMMER/FALL).
        year (int): The year the anime aired.
        producers (list): A list of the producers.
        licensors (list): A list of the licensors.
        studios (list): A list of studios.
        source (str): The source material for the anime.
        genres (list): A list of genres.
        theme (str): The theme of the anime.
        demographic (str): The demographic of the anime (i.e. Shounen).
        duration (str): The average duration of the anime.
        rating (str): The rating of the anime.
    """

    __slots__ = ("id", "title", "english", "synonyms", "japanese", "type",
                "episodes", "status", "aired", "season", "year", "producers",
                "licensors", "studios", "source", "genres", "theme", "demographic",
                "duration", "rating")

    def __init__(self, data:tuple):
        """
        The constructor of the Anime class.
        
        Parameters
        ----------
            data: A tuple containing a numerical id and a
                requests.Response object
        """
        _attrs = self.parse_page(data)

        self.id = _attrs.get("id")
        self.title = _attrs.get("title")
        self.english = _attrs.get("english", [])
        self.synonyms = _attrs.get("synonyms", [])
        self.japanese = _attrs.get("japanese", [])
        self.type = _attrs.get("type")
        self.episodes = _attrs.get("episodes", 0)
        self.status = _attrs.get("status")
        self.aired = _attrs.get("aired", "")
        self.season = _attrs.get("season", "")
        self.year = _attrs.get("year", "")
        self.producers = _attrs.get("producers", [])
        self.licensors = _attrs.get("licensors", [])
        self.studios = _attrs.get("studios", [])
        self.source = _attrs.get("source", "")
        self.genres = _attrs.get("genres", [])
        self.theme = _attrs.get("theme", "")
        self.demographic = _attrs.get("demographic", "")
        self.duration = _attrs.get("duration", "")
        self.rating = _attrs.get("rating", "")

    def __str__(self):
        return f"{self.id} <{self.title}>"
    
    def __hash__(self):
        return hash(self.id)
    
    def get_titles(self) -> list:
        """Returns a unique list of alternative titles for
        the anime. Order not preserved."""
        return list(set([self.title] + self.english + self.synonyms + self.japanese))

    def get_english(self) -> list:
        """Returns the english name of the anime."""
        return self.english

    def get_alt(self) -> list:
        """Returns synonyms of the title."""
        return self.synonyms

    def get_native(self) -> list:
        """Returns the native spelling of the title."""
        return self.japanese if self.japanese else self.english
    
    def add_alt(self, alt_title:str) -> None:
        """
        Appends another alternative to the list of alternative titles."""
        if alt_title in self.get_titles(): self.synonyms.append(alt_title)
        
    def gather_data(self) -> dict:
        """Returns a dict of all the relevant data for the anime."""
        return {
            "id": self.id, "title": self.title,
            "english": self.english, "synonyms": self.synonyms, "japanese": self.japanese,
            "type": self.type, "episodes": self.episodes, "status": self.status,
            "aired": self.aired, "season": self.season, "year": self.year,
            "producers": self.producers, "licensors": self.licensors, "studios": self.studios,
            "source": self.source,
            "genres": self.genres, "theme": self.theme, "demographic": self.demographic,
            "duration": self.duration,
            "rating": self.rating,
        }

    def parse_page(self, data:tuple) -> dict:
        """Parses a given html containing data from an anime.
        
        Given a resquests.Session object, parse the html and
        return all relevant information.
        
        Parameters
        ----------
        data: A tuple containing a numerical id and a requests.Response
            object containing the html for a webpage.

        Returns
        -------
        metadata_dict: A dictionary containing data scraped from the give
            data.
        """
        soup = BeautifulSoup(data.content, "html.parser")
        
        metadata_dict = {"id": utils.get_id(data.url)}

        metadata_dict["title"] = soup.select_one('h1[class="title-name h1_bold_none"]').text

        for elem in soup.select("div[class='spaceit_pad']"):
            # Skip over irrelevant data
            if (len(elem.contents) < 2) or ('<span class="dark_text">' not in str(elem.contents[1])):
                continue
            
            # Clean the data to make it easier to organize
            data_contents = []
            for content in elem.contents:
                if type(content) == bs4.element.NavigableString:
                    if (content.strip()):
                        data_contents.append(content.strip())
                else:
                    data_contents.append(content)

            # What kind of the information is it
            data_type_tag = data_contents[0]
            data_type = data_type_tag.text.replace(":", "").strip().lower()

            # Exclude certain pieces of data
            # if data_type in ["ranked", "members", "favorites", "score", "broadcast"]: continue
            
            if elem.select("a[href^='/anime/']") != []:
                data = [piece.text for piece in elem.select("a[href^='/anime/']")]
            else:
                # Handle case where only either the data or data type is provided
                if len(data_contents) < 2: continue

                if type(data_contents[1]) == str:
                    data = data_contents[1]
                else:
                    data = data_contents[1].text

            if type(data) == str:
                # Normalize marking for unknown data
                data = "" if data.rstrip(",") in ("None found", "None", "N/A") else data.rstrip(",")
            
            metadata_dict[data_type.lower()] = [data] if data_type in ["english", "japanese", "native", "synonyms", "synonym"] else data

        # In case of anime with only one genre
        if ("genre" in metadata_dict.keys()) and ("genres" not in metadata_dict.keys()):
            metadata_dict["genres"] = metadata_dict.pop("genre")
        elif ("genre" not in metadata_dict.keys()) and ("genres" not in metadata_dict.keys()):
            metadata_dict["genres"] = []

        if ("premiered" in metadata_dict.keys()) and (len(metadata_dict["premiered"].split()) > 1):
            metadata_dict["season"], metadata_dict["year"] = metadata_dict.pop("premiered").split()

        return metadata_dict

    def refresh_data(self, webdriver=None) -> None:
        """Update the class attributes (title, status, etc.) using the
        anime id to (re)download the data from MyAnimeList.
        
        Parameters
        ----------
            webdriver (requests.Session): The webdriver for navigating
                webpages.
        
        Returns
        -------
            None
        """
        if not webdriver:
            req = download("https://myanimelist.net/anime/" + self.id)
        else:
            req = download("https://myanimelist.net/anime/" + self.id, webdriver)

        if not req.ok: return   # Skip bad requests

        data = self.parse_page((self.id, req.content))

        self.id = data.get("id")
        self.title = data.get("title")
        self.english = data.get("english", [])
        self.synonyms = data.get("synonyms", [])
        self.japanese = data.get("japanese", [])
        self.type = data.get("type")
        self.episodes = data.get("episodes", 0)
        self.status = data.get("status")
        self.aired = data.get("aired", "")
        self.season = data.get("season", "")
        self.year = data.get("year", "")
        self.producers = data.get("producers", [])
        self.licensors = data.get("licensors", [])
        self.studios = data.get("studios", [])
        self.source = data.get("source", "")
        self.genres = data.get("genres", [])
        self.theme = data.get("theme", "")
        self.demographic = data.get("demographic", "")
        self.duration = data.get("duration", "")
        self.rating = data.get("rating", "")