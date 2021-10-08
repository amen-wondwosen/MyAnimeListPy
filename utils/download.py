"""
@author: Amen Wondwosen
"""
import time
import urllib.request

from bs4 import BeautifulSoup
import requests
from selenium import webdriver

MIN_MAL_TIME = 4    # min wait time to avoid MAL error

def download(url, driver=requests.session(), wait_time=MIN_MAL_TIME):
    req = driver.get(url)
    time.sleep(wait_time)

    return req


if __name__ == '__main__':
    # url = "https://myanimelist.net/anime/16067/"
    url = "https://myanimelist.net/anime.php?letter=B&show=0"

    req = download(url)
    resp = req.content
    # print(req)
    # with open("./sample_html.html", "w+", encoding="utf-8") as outfile:
    #     outfile.write(str(req))

    soup = BeautifulSoup(resp, "html.parser")
    for elem in soup.select("a[id^='sinfo']"):
        title = elem.select_one("strong").text
        MAL_id = elem["href"]
        print(title)
        print(MAL_id)
        print("-----------------")