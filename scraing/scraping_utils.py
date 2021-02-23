#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
print(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))+"/processing")
from preprocess import create_conversion_dict  # nopep8


def get_soup(url: str, sleep_sec=3):
    response = requests.get(url)
    time.sleep(sleep_sec)
    return BeautifulSoup(response.text, 'html.parser')


def set_driver():
    # Set driver
    opt = Options()
    opt.add_argument('--headless')
    # Open browser
    driver = webdriver.Chrome(options=opt)
    return driver


def scraping_from_navitime(category_id: str, pref_code_list: list) -> pd.DataFrame:
    # Load pref data
    pref_path = "/home/vagrant/share/data/station/pref.csv"
    df_pref = pd.read_csv(pref_path)
    pref_code_to_name = create_conversion_dict(df_pref, 'pref')

    # Get info
    pref_code_list = [i for i in range(11, 15)]
    main_url = "https://www.navitime.co.jp/category/{0}/{1}/?page={2}"
    info_list = []
    for pref_code in pref_code_list:
        pref = pref_code_to_name[pref_code]
        page_id = 1
        while True:
            print(f"{pref}, page_id: {page_id}")
            soup = get_soup(main_url.format(category_id, pref_code, page_id))
            spot_contents = soup(class_="spot-content")
            if len(spot_contents) <= 1:
                break
            for sc in spot_contents[1:]:
                info_dict = {}
                info_dict['name'] = sc(
                    class_="spot-name")[0].text.replace("\n", "").replace("\t", "")
                info_dict['address'] = sc(
                    class_="spot-detail-value")[0].text
                info_dict['pref'] = pref
                info_list.append(info_dict)
            page_id += 1
        print("")

    return pd.DataFrame(info_list)
