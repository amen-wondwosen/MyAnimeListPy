from urllib.parse import urlparse


def get_id(url):
    '''
    Separates the path of the url and get the
    second part of the path (the MAL ID).
    Ex.
        https://myanimelist.net/anime/12031/Kingdom
        returns 12031
    '''
    return urlparse(url).path.split('/')[2]


def combine_sources(mal, al):
    '''
    Joins metadata from MyAnimeList and AniList
    and removes any redundant data. Returns a
    dict object containing the newly joined data.
    '''

    if "errors" in al.keys():
        # If no metadata from anilist
        return mal_all(mal)

    # For simplicity
    al = al["data"]["Media"]

    j_data = {
        "idMal": "", "idAL": "", "title": "",
        "english": [], "japanese": [], "romaji": [], "synonyms": [], "native": [],
        "type": "",
        "episodes": 0, "status": "", "aired": "???", "season": "", "year": "",
        "demographic": "", "genres": [], "tags": [], "theme": "",
        "source": "",
        "licensors": [], "studios": [],
        "rating": ""
    }

    j_data["idMal"] = mal["id"]
    j_data["idAL"] = str(al["id"])

    j_data["title"] = mal["title"]

    j_data["english"] += mal.get("english", [])
    if al["title"]["english"]: j_data["english"].append(al["title"]["english"])

    j_data["japanese"] += mal.get("japanese", [])

    j_data["romaji"].append(al["title"].get("romaji", []))

    j_data["synonyms"] += mal.get("synonyms", [])

    if al["title"]["native"]: j_data["native"] = al["title"]["native"]

    j_data["type"] = mal["type"]

    j_data["episodes"] = mal["episodes"]

    j_data["status"] = mal["status"]

    j_data["aired"] = mal["aired"]

    j_data["season"] = al["season"]
    j_data["year"] = al["seasonYear"]

    j_data["demographic"] = mal.get("demographic", "")

    j_data["genres"] = list(set(mal["genres"] + al["genres"]))
    j_data["tags"] = [node["name"] for node in al["tags"]]
    j_data["theme"] = mal.get("theme", "")
    
    j_data["source"] = mal["source"]

    if mal["licensors"] != "None found":
        if type(mal["licensors"]) == str:
            j_data["licensors"].append(mal["licensors"])
        else:
            j_data["licensors"] = mal["licensors"]

    for edge in al["studios"]["edges"]:
        j_data["studios"].append(edge["node"]["name"])

    j_data["rating"] = mal["rating"]

    return j_data


def mal_all(mal):
    '''
    Reformats the mal data into the same format as
    shown in the combine_sources function
    '''
    j_data = {
        "idMal": "", "idAL": "", "title": "",
        "english": [], "japanese": [], "romaji": [], "synonyms": [], "native": [],
        "type": "",
        "episodes": 0, "status": "", "aired": "", "season": "", "year": "",
        "demographic": "", "genres": [], "tags": [], "theme": "",
        "source": "",
        "licensors": [], "studios": [],
        "rating": ""
    }

    j_data["idMal"] = mal["id"]

    j_data["title"] = mal["title"]

    j_data["english"] += mal.get("english", [])

    j_data["japanese"] += mal.get("japanese", [])

    j_data["synonyms"] += mal.get("synonyms", [])

    j_data["type"] = mal["type"]

    j_data["episodes"] = mal["episodes"]

    j_data["status"] = mal["status"]

    if "premiered" in mal.keys():
        j_data["season"], j_data["year"] = mal["premiered"].split()

    j_data["demographic"] = mal.get("demographic", "")

    j_data["genres"] = mal["genres"]
    j_data["theme"] = mal.get("theme", "")
    
    j_data["source"] = mal["source"]

    if mal["licensors"] != "None found":
        if type(mal["licensors"]) == str:
            j_data["licensors"].append(mal["licensors"])
        else:
            j_data["licensors"] = mal["licensors"]

    j_data["studios"] = mal.get("studios", [])

    j_data["rating"] = mal["rating"]

    return j_data