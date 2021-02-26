#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
import json
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))+"/../processing/")
from preprocess import full_to_harf_width_char  # nopep8
from scraping_utils import get_soup, set_driver  # nopep8


def get_restarant_soup(station, url=None):
    driver = set_driver()
    if url:
        driver.get(url)
    else:
        driver = set_driver()
        url = "https://tabelog.com"
        driver.get(url)
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, "sa")))
        driver.find_element_by_css_selector("#sa").send_keys(station)
        driver.find_element_by_id('js-global-search-btn').click()
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, "list")))

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup


def create_number_of_restaurant_dict(soup):
    restaurant_dict = {}
    tmp_soup = soup(class_="list-balloon__sub-list-item--4column")
    for t in tmp_soup:
        restaurant_dict[t('span')[0].text] = int(t('span')[1].text[1:-2])
    return restaurant_dict


def get_number_of_restaurants(station, check_station):
    soup = get_restarant_soup(station)
    # Check page in station name
    check_word = soup.select(
        "#container > div.rstlist-contents.clearfix > div.flexible-rstlst > div > div.list-condition.list-condition--flexible > div.list-condition__header > h2 > strong")[0].text
    if full_to_harf_width_char(check_word) == check_station + "のお店":
        # Get number of restaurants around the station
        return create_number_of_restaurant_dict(soup)
    else:
        suggest_station = soup.select(
            "#container > div.rstlist-contents.clearfix > div.flexible-rstlst > div > div.search-suggest > ul > li")
        if suggest_station:
            for ss in suggest_station:
                if ss.text == check_station:
                    url = ss('a')[0].get('href')
                    break
            soup = get_restarant_soup(station, url)
            return create_number_of_restaurant_dict(soup)
        else:
            print(f"check_station:{check_station}, check_word:{check_word}")
            return None


if __name__ == '__main__':
    # Load data
    data_path = '../../data/'
    station_info_dict_path = data_path + "station_info_dict.json"
    if os.path.exists(station_info_dict_path):
        with open(station_info_dict_path, 'r') as f:
            station_name_dict = json.load(f)
        station_list = [k for k, v in station_name_dict.items()
                        if not 'num_restaurant' in v.keys()]
    else:
        station_name_dict_path = data_path + 'station_name_dict.json'
        with open(station_name_dict_path, 'r') as f:
            station_name_dict = json.load(f)
        station_list = [k for k in station_name_dict.keys()]

    # Get number of restaurants around the station

    print(f"total station length: {len(station_list)}")
    for i, s in enumerate(station_list):
        print(i+1, s)
        start = time.time()
        if "(" in s:
            num = s.find("(")
            station = s[:num] + "駅"
            check_station = station + s[num:]
        else:
            station = s + "駅"
            check_station = s + "駅"
        restaurant_dict = get_number_of_restaurants(station, check_station)
        if restaurant_dict:
            station_name_dict[s]["num_restaurant"] = restaurant_dict

        elapsed_time = time.time() - start
        print(f"elapsed_time:{elapsed_time}[sec]")
        if i != 0 and i % 3 == 0:
            with open(station_info_dict_path, 'w') as f:
                json.dump(station_name_dict, f, indent=4, ensure_ascii=False)
            print("Save info until now")

    # Save station_num_restaurant_dict
    with open(station_info_dict_path, 'w') as f:
        json.dump(station_name_dict, f, indent=4, ensure_ascii=False)
    print("Done!")
