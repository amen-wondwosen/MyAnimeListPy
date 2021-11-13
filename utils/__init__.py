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