#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
import datetime
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraping_utils import *  # nopep8


class GetRentalProperty:
    def __init__(self):
        self.this_year = datetime.date.today().year

    @staticmethod
    def area_urls(pref_dict: dict):
        main_url = "https://www.homes.co.jp/chintai/{}/city/"
        area_urls = {}

        for pref in pref_dict.keys():
            area_urls[pref_dict[pref]] = {}
            if pref == "tokyo":
                driver = set_driver()
                driver.get(main_url.format(pref))
                WebDriverWait(driver, 30).until(
                    EC.visibility_of_element_located((By.ID, "contents")))
                response = driver.find_element_by_css_selector(
                    "#prg-flowform > div.mod-tokyoCityList.area.fitting")
                soup = BeautifulSoup(response.get_attribute(
                    'innerHTML'), 'html.parser')
                url_list = soup.select(
                    'fieldset > div.prg-setBukkenCond > ul > li > a')
            else:
                soup = get_soup(main_url.format(pref))
                url_list = soup.select(
                    '#prg-flowform > div.mod-checkList.area.fitting > fieldset> div.prg-setBukkenCond > ul > li > a')

            for url in url_list:
                area_urls[pref_dict[pref]][url.text] = url.get('href')

        return area_urls

    def property_info(self, soup, pref: str, mun: str, property_list: list):
        # Add property info
        property_dict = {}
        spec_info = soup(class_='bukkenSpec')[0]('td')
        access_info = spec_info[1]('span')
        etc_info = spec_info[2].text.split(' / ')
        property_dict['type'] = soup(
            class_='bType')[0].text.replace('賃貸', '')
        property_dict['name'] = soup(class_='bukkenName')[0].text
        property_dict['address'] = spec_info[0].text
        property_dict['prefectures'] = pref
        property_dict['municipality'] = mun
        property_dict['access'] = [ai.text for ai in access_info]
        if etc_info[0] == '新築':
            property_dict['year_built'] = self.this_year
        else:
            property_dict['year_built'] = self.this_year - \
                int(etc_info[0].strip('年'))
        try:
            property_dict['story'] = int(etc_info[1].strip('階建'))
        except:
            property_dict['story'] = 1

        # Add unit info
        unit_list = []
        unit_info = soup(class_='unitSummary')[0]
        for i, u in enumerate(unit_info(class_='prg-room')):
            if i % 2 == 0:
                unit_dict = {}
                price_info = u(class_='price')[0].text.split('/')
                layout_info = u(class_='layout')[0].text

                # Add floor info
                try:
                    unit_dict['floor'] = int(u(class_='roomKaisuu')[
                                             0].text.replace('階', ''))
                except:
                    unit_dict['floor'] = 1

                # Add price info
                unit_dict['rent'] = int(
                    float(price_info[0].strip('万円')) * 10000)
                if price_info[1][0] == '-':
                    unit_dict['manegement_fee'] = 0
                    unit_dict['security_deposit'] = price_info[1][1:]
                elif '円' in price_info[1]:
                    tmp = price_info[1].split('円')
                    unit_dict['security_deposit'] = tmp[1]
                    if '万' in tmp[0]:
                        unit_dict['manegement_fee'] = int(
                            float(tmp[0].strip('万')) * 10000)
                    else:
                        unit_dict['manegement_fee'] = int(
                            tmp[0].replace(',', ''))
                else:
                    print(
                        f"property_name: {property_dict['name']}, price_info: {price_info[1]}")

                unit_dict['key_money'] = price_info[2]

                # Add layout info
                if 'ワンルーム' in layout_info:
                    unit_dict['floor_plan'] = '1R'
                    occupied_area = layout_info.replace('ワンルーム', '')
                else:
                    unit_dict['floor_plan'] = layout_info.split('K')[0] + 'K'
                    occupied_area = layout_info.split('K')[1]
                try:
                    unit_dict['occupied_area'] = float(
                        occupied_area.replace('m²', ''))
                except:
                    continue

                # Add condition info
                try:
                    conditions = unit_info(
                        class_='prg-relatedKeywordsRow')[int(i / 2)]
                    unit_dict['conditions'] = [
                        c.text for c in conditions(class_='relatedKeyword')]
                except:
                    unit_dict['conditions'] = None

                unit_list.append(unit_dict)

        property_dict['number_of_units'] = len(unit_list)
        property_dict['units'] = unit_list
        property_list.append(property_dict)

        return property_list
