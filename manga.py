from collections import defaultdict
import time

import bs4
from bs4 import BeautifulSoup

from . import utils
from .utils.download import download

class DuplicateTitleError(Exception):
    pass


class Manga:
    __slots__ = ("client", "id", "title", "english", "synonyms", "japanese", "type",
                "volumes", "chapters", "status", "published", "producers",
                "licensors", "studios", "source", "genres", "theme", "demographic",
                "serialization", "authors")

    def __init__(self, data):
        _attrs = self.parse_page(data)

        for k, val in _attrs.items():
            print(f"{k} -> {val}")
            print("-------------")

        self.id = _attrs.get("id")
        self.title = _attrs.get("title")
        self.english = _attrs.get("english", [])
        self.synonyms = _attrs.get("synonyms", [])
        self.japanese = _attrs.get("japanese", [])
        self.type = _attrs.get("type")
        self.volumes = _attrs.get("volumes", "0")
        self.chapters = _attrs.get("chapters", "0")
        self.status = _attrs.get("status")
        self.published = _attrs.get("published", "Unknown")
        self.producers = _attrs.get("producers", [])
        self.licensors = _attrs.get("licensors", [])
        self.studios = _attrs.get("studios", [])
        self.source = _attrs.get("source", "Unknown")
        self.genres = _attrs.get("genres", [])
        self.theme = _attrs.get("theme", "Unknown")
        self.demographic = _attrs.get("demographic", "Unknown")
        self.serialization = _attrs.get("", "Unknown")
        self.authors = _attrs.get("authors", [])
    
    def get_titles(self):
        """Returns a unique list of alternative titles for
        the anime. Order not guaranteed."""
        return list(set([self.title] + self.english + self.synonyms + self.japanese))

    def get_english(self):
        """Returns the english name of the anime."""
        return self.english

    def get_alt(self):
        """Returns synonyms of the title."""
        return self.synonyms

    def get_native(self):
        """Returns the native spelling of the title."""
        return self.japanese if self.japanese else self.english
    
    def add_alt(self, alt_title):
        """
        Appends another alternative to the list of alternative titles.
        
        Raises DuplicateTitleError if the title is already known.
        """
        if alt_title in self.get_titles():
            raise DuplicateTitleError
        else:
            self.synonyms.append(alt_title)
        
    def gather_data(self):
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

    def parse_page(self, data):
        '''
        @param data: (id, html containing anime data)
        Parses a given html containing data from an
        anime. Extract from the html:
            - English version of title
            - Any synonyms of title
            - Japanese version (if any) of title
            - Published date
            - Volume count
            - Chapter count
            - Type of media (ie. Manga, Light Novel, etc.)
            - Tags
            - As well as any other relevant metadata
        '''
        # A list of data types that could contain multiple values
        multi_data_types = ["english", "japanese", "native", "synonyms", "synonym"]

        soup = BeautifulSoup(data.text, "html.parser")
        
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

        # Normalize Japanese names to first name first format
        if ("author" in metadata_dict.keys()) and ("authors" not in metadata_dict.keys()):
            metadata_dict["authors"] = metadata_dict.pop("author")
        elif ("author" not in metadata_dict.keys()) and ("authors" not in metadata_dict.keys()):
            metadata_dict["authors"] = []

        # Use the premiered attribute to find the season and year
        if ("premiered" in metadata_dict.keys()) and (len(metadata_dict["premiered"].split()) > 1):
            metadata_dict["season"], metadata_dict["year"] = metadata_dict.pop("premiered").split()

        return metadata_dict

    def __str__(self) -> str:
        return f"{self.id} <{self.title}>"
    
    def __hash__(self) -> int:
        return hash(self.id)