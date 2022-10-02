import re
import time
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko"
}


def fetch_soup(url, parser="html.parser"):

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    soup = BeautifulSoup(r.content, parser)

    return soup


def fetch_area(url):

    soup = fetch_soup(url)
    area = soup.select_one("h2#sagasu_chiku").find_next_sibling("div", class_="box")

    result = [
        urljoin(url, tag.get("href")) for tag in area.select("ul.sagasu_list > li > a")
    ]

    return result


url = "https://imabari-pcoupon.jp/kamei/?index"

links = fetch_area(url)

data = []

for link in links:

    soup = fetch_soup(link)

    for i in soup.select("ul.kekka_ichiran > li > a"):

        shop = {}

        tag = i.get("href")

        m = re.search("id=(\d+)", tag)

        shop["id"] = int(m.group(1)) if m else None
        shop["name"] = i.select_one("strong.kekka_tenmei").get_text(strip=True)
        shop["area"] = i.select_one("span.kekka_area").get_text(strip=True)
        shop["food"] = i.select_one("span.kekka_gyotai").get_text(strip=True)
        shop["takeout"] = i.select_one("span.kekka_takeout").get_text(strip=True)
        shop["url"] = urljoin(url, tag)

        data.append(shop)

    time.sleep(3)


df = pd.DataFrame(data).set_index("id").sort_index()

df.to_csv("./html/imabari-coupon.csv", encoding="utf_8_sig", index=False)
