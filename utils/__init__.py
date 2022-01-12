from urllib.parse import urlparse

def get_id(url:str):
    """Extracts the mal id from the url."""
    return urlparse(url).path.split('/')[2]