import time

import bs4
from bs4 import BeautifulSoup

from . import utils
from .utils.download import download

class Manga:
    """This is a class for gathering data scrapped from webpages
    containing seasonal from MyAnimeList manga pages.

    Attributes
    -----------
        id (int|str): A uid for representing an manga on MyAnimeList.
        title (str): The title of the manga.
        english (list): A list of english names.
        synonyms (list): A list of alternative names.
        japanese (list): A list of japanese/native names.
        type (str): The type of media (Manga, Light Novel, etc.).
        volumes (int): The number of volumes of the manga.
        chapters (int): The number of chapters in the manga.
        status (str): The airing status of the manga.
        published (str): When the manga was first published.
        genres (list): A list of genres.
        theme (str): The theme of the anime.
        demographic (str): The demographic of the anime (i.e. Shounen).
        serialization (str): Where the manga is serialized (i.e. Shounen Jump).
        authors (list): A list of authors for the manga.
    """

    __slots__ = ("id", "title", "english", "synonyms", "japanese", "type",
                "volumes", "chapters", "status", "published",
                "genres", "theme", "demographic",
                "serialization", "authors")

    def __init__(self, data):
        """"""
        _attrs = self.parse_page(data)

        self.id = _attrs.get("id")
        self.title = _attrs.get("title")
        self.english = _attrs.get("english", [])
        self.synonyms = _attrs.get("synonyms", [])
        self.japanese = _attrs.get("japanese", [])
        self.type = _attrs.get("type")
        self.volumes = _attrs.get("volumes", 0)
        self.chapters = _attrs.get("chapters", 0)
        self.status = _attrs.get("status")
        self.published = _attrs.get("published", "Unknown")
        self.genres = _attrs.get("genres", [])
        self.theme = _attrs.get("theme", "Unknown")
        self.demographic = _attrs.get("demographic", "Unknown")
        self.serialization = _attrs.get("", "Unknown")
        self.authors = _attrs.get("authors", [])
    
    def __str__(self) -> str:
        return f"{self.id} <{self.title}>"
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def get_titles(self):
        """Returns a unique list of alternative titles for
        the manga. Order not preserved."""
        return list(set([self.title] + self.english + self.synonyms + self.japanese))

    def get_english(self):
        """Returns the english name of the manga."""
        return self.english

    def get_alt(self):
        """Returns synonyms of the title."""
        return self.synonyms

    def get_native(self):
        """Returns the native spelling of the title."""
        return self.japanese if self.japanese else self.english
    
    def add_alt(self, alt_title) -> None:
        """Appends another alternative to the list of alternative titles."""
        if alt_title not in self.get_titles(): self.synonyms.append(alt_title)
        
    def gather_data(self) -> dict:
        """Returns a dict of all the relevant data for the manga."""
        return {
            "id": self.id, "title": self.title,
            "english": self.english, "synonyms": self.synonyms, "japanese": self.japanese,
            "type": self.type, "volumes": self.volumes, "chapters": self.chapters, "status": self.status,
            "published": self.published,
            "genres": self.genres, "theme": self.theme, "demographic": self.demographic,
            "serialization": self.serialization,
            "authors": self.authors,
        }

    def parse_page(self, data:tuple) -> dict:
        """Parses a given html containing data from a manga.
        
        Given a resquests.Session object, parse the html and
        return all relevant information.
        
        Parameters
        ----------
            data: A tuple containing a numerical id and a
                requests.Response object containing the html for a webpage.
            
        Returns
        -------
            metadata_dict: A dictionary containing data scraped from
                the given data.
        """
        # A list of data types that could contain multiple values
        multi_data_types = ["english", "japanese", "native", "synonyms", "synonym"]

        soup = BeautifulSoup(data.content, "html.parser")
        
        metadata_dict = {"id": utils.get_id(data.url)}

        metadata_dict["title"] = soup.select_one('h1[class="h1 edit-info"] > span').text

        for elem in soup.select("div[class='spaceit_pad']"):
            # Skip over irrelevant data
            if (len(elem.contents) < 2) or (not soup.select('span[class="dark_text"]')):
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

            if elem.select("a[href^='/manga/']") != []:
                data = [piece.text.strip() for piece in elem.select("a[href^='/manga/']")]
            elif elem.select("a[href^='/people/']") != []:
                data = [piece.text.strip() for piece in elem.select("a[href^='/people/']")]
            else:
                # Handle case where only either the data or data type is provided
                if len(data_contents) < 2: continue

                if type(data_contents[1]) == str:
                    data = data_contents[1]
                else:
                    data = data_contents[1].text

            if type(data) == str:
                # Normalize marking for unknown data
                data = data if data not in ("None found", "None", "N/A") else "Unknown"
            
            metadata_dict[data_type.lower()] = [data] if data_type in multi_data_types else data

        # In case of anime with only one genre
        if ("genre" in metadata_dict.keys()) and ("genres" not in metadata_dict.keys()):
            metadata_dict["genres"] = metadata_dict.pop("genre")
        elif ("genre" not in metadata_dict.keys()) and ("genres" not in metadata_dict.keys()):
            metadata_dict["genres"] = []

        # In case of anime with only one genre
        if ("author" in metadata_dict.keys()) and ("authors" not in metadata_dict.keys()):
            metadata_dict["authors"] = metadata_dict.pop("author")
        elif ("author" not in metadata_dict.keys()) and ("authors" not in metadata_dict.keys()):
            metadata_dict["authors"] = []

        # Use the premiered attribute to find the season and year
        if ("premiered" in metadata_dict.keys()) and (len(metadata_dict["premiered"].split()) > 1):
            metadata_dict["season"], metadata_dict["year"] = metadata_dict.pop("premiered").split()

        return metadata_dict
    
    def refresh_data(self, webdriver=None) -> None:
        """Update the class attributes (title, status, etc.) using the
        manga id to (re)download the data from MyAnimeList.
        
        Parameters
        ----------
            webdriver (requests.Session): The webdriver for navigating
                webpages.
        
        Returns
        -------
            None
        """
        if not webdriver:
            req = download("https://myanimelist.net/manga/" + self.id)
        else:
            req = download("https://myanimelist.net/manga/" + self.id, webdriver)

        if not req.ok: return   # Skip bad requests

        data = self.parse_page((self.id, req.content))

        self.id = data.get("id")
        self.title = data.get("title")
        self.english = data.get("english", [])
        self.synonyms = data.get("synonyms", [])
        self.japanese = data.get("japanese", [])
        self.type = data.get("type")
        self.volumes = data.get("volumes", "0")
        self.chapters = data.get("chapters", "0")
        self.status = data.get("status")
        self.published = data.get("published", "Unknown")
        self.genres = data.get("genres", [])
        self.theme = data.get("theme", "Unknown")
        self.demographic = data.get("demographic", "Unknown")
        self.serialization = data.get("", "Unknown")
        self.authors = data.get("authors", [])