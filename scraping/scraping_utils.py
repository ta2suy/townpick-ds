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
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))+"/processing")
from preprocess import create_conversion_dict  # nopep8


def get_soup(url: str, sleep_sec=3):
    response = requests.get(url)
    time.sleep(sleep_sec)
    return BeautifulSoup(response.content, 'html.parser')


def set_driver():
    # Set driver
    opt = Options()
    opt.add_argument('--headless')
    # Open browser
    driver = webdriver.Chrome(options=opt)
    return driver


def get_pref_code_to_name():
    # Load pref data
    pref_path = "/home/vagrant/share/data/station/pref.csv"
    df_pref = pd.read_csv(pref_path)
    return create_conversion_dict(df_pref, 'pref')


def scraping_from_navitime(category_id: str, pref_code_list: list) -> pd.DataFrame:
    pref_code_to_name = get_pref_code_to_name()

    # Get info
    main_url = "https://www.navitime.co.jp/category/{0}/{1}/?page={2}"
    info_list = []
    for pref_code in pref_code_list:
        pref = pref_code_to_name[pref_code]
        page_id = 1
        while True:
            print(f"{pref}, page_id: {page_id}")
            soup = get_soup(main_url.format(
                category_id, str(pref_code).zfill(2), page_id))
            spot_contents = soup(class_="spot-content")
            if len(spot_contents) <= 1:
                break
            for sc in spot_contents[1:]:
                info_dict = {}
                info_dict['name'] = sc(
                    class_="spot-name")[0].text.replace("\n", "").replace("\t", "").replace("\u3000","")
                info_dict['address'] = sc(
                    class_="spot-detail-value")[0].text
                info_dict['pref'] = pref
                info_list.append(info_dict)
            page_id += 1
        print("")

    return pd.DataFrame(info_list)


def scraping_from_mapfan(category_id: str, pref_code_list: list) -> pd.DataFrame:
    pref_code_to_name = get_pref_code_to_name()

    # Get info
    main_url = "https://mapfan.com/genres/{0}/{1}/"
    info_list = []
    for pref_code in pref_code_list:
        pref = pref_code_to_name[pref_code]
        soup = get_soup(main_url.format(category_id, str(pref_code).zfill(2)))
        mun_urls = soup(class_="list ng-star-inserted")[0]('a')
        for mu in mun_urls:
            mun = mu.text.split(" ")[0]
            url = "https://mapfan.com" + mu.get('href')
            print(f"pref: {pref}, mun:{mun}")
            page_id = 1
            while True:
                soup = get_soup(url + "?page={}".format(page_id))
                facility_list = soup(
                    class_="mat-list-item mat-focus-indicator mat-3-line mat-list-item-avatar mat-list-item-with-avatar ng-star-inserted")
                if len(facility_list) == 0:
                    break
                else:
                    page_id += 1
                for facility in facility_list:
                    info_dict = {}
                    name = facility(
                        class_="mat-line name mat-subheading-1")[0].text.replace("\u3000", "")
                    while name[0] == " ":
                        name = name[1:]
                    info_dict['name'] = name
                    info_dict['address'] = facility(
                        class_="mat-line address")[0].text
                    info_dict['category'] = facility(class_='mat-line genre-name ng-star-inserted')[
                        0].text.replace(" ", "").replace("[", "").replace("]", "")
                    info_dict['pref'] = pref
                    info_dict['mun'] = mun
                    info_list.append(info_dict)
        print("")

    return pd.DataFrame(info_list)
