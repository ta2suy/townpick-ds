#!/usr/bin/env python
# coding: utf-8

import os
import sys
import json
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


class GetNumRestaurant:
    def __init__(self):
        self.driver = set_driver()

    def load_dataset(self):
        restaurant_path = '/home/vagrant/share/data/restaurant/'
        self.num_restaurant_dict_path = restaurant_path + "num_restaurant.json"
        if os.path.exists(self.num_restaurant_dict_path):
            with open(self.num_restaurant_dict_path, 'r') as f:
                num_restaurant_dict = json.load(f)
            print("load num_restaurant_dict")
        else:
            with open('../../data/station_name_dict.json', 'r') as f:
                station_name_dict = json.load(f)
            num_restaurant_dict = {k:{} for k in station_name_dict.keys()}
            num_restaurant_dict = {k: {} for k in station_name_dict.keys()}

        station_list = [k for k, v in num_restaurant_dict.items(
        ) if not 'num_restaurant' in v]

        self.unfound_station_dict_path = restaurant_path + \
            "unfound_station_in_restaurant.json"
        if os.path.exists(self.unfound_station_dict_path):
            with open(self.unfound_station_dict_path, 'r') as f:
                unfound_station_dict = json.load(f)
        else:
            unfound_station_dict = {}

        return num_restaurant_dict, station_list, unfound_station_dict

    def get_restarant_soup(self, station, url=None):
        if url:
            self.driver.get(url)
        else:
            url = "https://tabelog.com"
            self.driver.get(url)
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, "sa")))
            self.driver.find_element_by_css_selector("#sa").send_keys(station)
            self.driver.find_element_by_id('js-global-search-btn').click()
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.ID, "list")))

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        return soup

    def create_number_of_restaurant_dict(self, soup):
        restaurant_dict = {}
        tmp_soup = soup(class_="list-balloon__sub-list-item--4column")
        for t in tmp_soup:
            distance = t('span')[0].text.split('[')[0]
            restaurant_dict[distance] = int(t('span')[1].text[1:-2])
        return restaurant_dict

    def get_number_of_restaurants(self, station, check_station, unfound_station_dict):
        soup = self.get_restarant_soup(station)
        # Check page in station name
        check_word = soup.select(
            "#container > div.rstlist-contents.clearfix > div.flexible-rstlst > div > div.list-condition.list-condition--flexible > div.list-condition__header > h2 > strong")[0].text
        if full_to_harf_width_char(check_word).replace('ケ', 'ヶ') == check_station + "のお店":
            # Get number of restaurants around the station
            return self.create_number_of_restaurant_dict(soup)
        else:
            suggest_station = soup.select(
                "#container > div.rstlist-contents.clearfix > div.flexible-rstlst > div > div.search-suggest > ul > li")
            if suggest_station:
                suggest_station_list = []
                for ss in suggest_station:
                    suggest_station_list.append(full_to_harf_width_char(
                        ss.text).replace('\n', '').replace('ケ', 'ヶ'))
                    if suggest_station_list[-1] == check_station:
                        url = ss('a')[0].get('href')
                        soup = self.get_restarant_soup(station, url)
                        return self.create_number_of_restaurant_dict(soup)
                unfound_station_dict[check_station] = suggest_station_list
                return None
            else:
                unfound_station_dict[check_station] = check_word
                print(
                    f"check_station:{check_station}, check_word:{check_word}")
                return None

    def save_dict(self, num_restaurant_dict, unfound_station_dict):
        with open(self.num_restaurant_dict_path, 'w') as f:
            json.dump(num_restaurant_dict, f, indent=4, ensure_ascii=False)
        with open(self.unfound_station_dict_path, 'w') as f:
            json.dump(unfound_station_dict, f,
                      indent=4, ensure_ascii=False)
