#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
import json
import pickle
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))+"/scraping/")
from scraping_utils import get_soup  # nopep8


def get_urls(pref_list):
    urls = []
    url = "https://geoshape.ex.nii.ac.jp/ka/resource/?{}"
    for p in pref_list:
        soup = get_soup(url.format(p))
        for tmp in soup(class_='list')[0]('tr'):
            if p in tmp.text:
                urls.append("https://geoshape.ex.nii.ac.jp/" +
                            tmp('td')[-1]('a')[0].get('href'))
    return urls


def get_key_latlon(urls):
    key_latlon = []
    for index, url in enumerate(urls):
        start = time.time()
        soup = get_soup(url)
        latlon_dict = json.loads(soup.text)
        tmp = latlon_dict['objects']['town']['geometries']
        for i in range(len(tmp)):
            t = tmp[i]['properties']
            key_latlon.append([t['KEY_CODE'], t['Y_CODE'], t['X_CODE']])
        elapsed_time = time.time() - start
        print(f"{index}, elapsed_time:{elapsed_time}[sec]")
    return key_latlon


if __name__ == '__main__':
    # Get urls
    pref_list = ["埼玉県", "千葉県", "東京都", "神奈川県"]
    urls = get_urls(pref_list)

    # Get key latlon
    print(f"total urls:{len(urls)}")
    key_latlon = get_key_latlon(urls)

    # Save
    path = "/home/vagrant/share/data/census/key_latlon.csv"
    df = pd.DataFrame(key_latlon, columns=['key_code', 'lat', 'lon'])
    df = df.groupby('key_code').mean()
    df.reset_index(inplace=True)
    df.to_csv(path, index=False)
    print("Done!")
