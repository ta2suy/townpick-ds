#!/usr/bin/env python
# coding: utf-8
import re
import time
import pickle
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from preprocess import remove_bracket


def set_driver():
    # Set driver
    opt = Options()
    opt.add_argument('--headless')

    # Open browser
    driver = webdriver.Chrome(options=opt)

    return driver


class LineStationInfo:
    def __init__(self, company_code_to_name: dict, line_code_to_name: dict, station_code_to_name: dict, pref_code_to_name: dict):
        self.line_station_info = []
        self.company_code_to_name = company_code_to_name
        self.line_code_to_name = line_code_to_name
        self.station_code_to_name = station_code_to_name
        self.pref_code_to_name = pref_code_to_name

    def add_station_info(self, company_cd, line_cd, line_type, first_station_cd, last_station_cd, first_station_pref_cd, last_station_pref_cd):
        company_name = self.company_code_to_name[company_cd]
        line_name = self.line_code_to_name[line_cd]
        first_station_name = self.station_code_to_name[first_station_cd]
        last_station_name = self.station_code_to_name[last_station_cd]
        first_station_pref = self.pref_code_to_name[first_station_pref_cd]
        last_station_pref = self.pref_code_to_name[last_station_pref_cd]

        # Remove '(xxx)'
        line_name = remove_bracket(line_name)
        first_station_name = remove_bracket(first_station_name)
        last_station_name = remove_bracket(last_station_name)

        # Add line station info
        self.line_station_info.append({
            'company_name': company_name,
            'company_code': company_cd,
            'line_name': line_name,
            'line_code': line_cd,
            'line_type': line_type,
            'first_station': first_station_name,
            'last_station': last_station_name,
            'first_station_pref': first_station_pref,
            'last_station_pref': last_station_pref
        })

    def save_info(self, path: str):
        df = pd.DataFrame(self.line_station_info)
        df.to_csv(path, index=False)


class GetUrls:
    @staticmethod
    def station_line(station: str, pref: str):
        driver = set_driver()
        url = 'https://transit.yahoo.co.jp/station/time'
        driver.get(url)
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, "obj_time_st")))
        driver.find_element_by_id('obj_time_st').send_keys(station + "駅")
        driver.find_element_by_class_name('btnSearch').click()
        WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located((By.ID, "main")))

        try:
            response = driver.find_element_by_id('mdSearchResult')
        except:
            return driver.current_url

        bs = BeautifulSoup(response.get_attribute(
            'innerHTML'), 'html.parser')
        tmp_list = []
        for l in bs('a'):
            tmp_list.append(l.text)
            if l.text == station or l.text == station+f'({pref})':
                return 'https://transit.yahoo.co.jp' + bs('a')[0].get('href')

        print(f'{station} dose not exist in {tmp_list}')
        return None

    @staticmethod
    def timetable(url: str, line_name: str, station: str):
        timetable_url = None
        response = requests.get(url)
        time.sleep(1)
        bs = BeautifulSoup(response.text, 'html.parser')
        links_in_line = bs(class_='elmSearchItem direction')[0]('dl')
        if 'JR' in line_name:
            line_name = line_name.replace('JR', 'ＪＲ')

        for ll in links_in_line:
            if line_name in ll('dt')[0].text:
                if len(ll('a')) == 1:
                    timetable_url = ll('a')[0].get('href')
                else:
                    for l in ll('a'):
                        print(l.text)
                        if station in l.text:
                            timetable_url = l.get('href')

        if timetable_url != None:
            timetable_url = 'https://transit.yahoo.co.jp/' + timetable_url

        return timetable_url


class GetTrainSchedule:
    def __init__(self):
        pass

    def train_schedule(self, timetable_url: str, line_type: str):
        response = requests.get(timetable_url)
        time.sleep(1)
        bs = BeautifulSoup(response.text, 'html.parser')
        destination_list = bs.select('#timeNotice2 li')
        destination_dict = self.destination_dict(destination_list)
        train_type_dict = self.train_type_dict(bs)
        df_train_schedule_url = self.train_schedule_url(
            bs, destination_dict, train_type_dict)

        # df_train_schedule_url.drop_duplicates(
        #     ['destination', 'train_type'], inplace=True)
        train_schedule_list = []
        duplicated_check_list = []
        timetable_id = 1
        for i in df_train_schedule_url.index:
            train_schedule_url = df_train_schedule_url.loc[i, 'url']
            destination = df_train_schedule_url.loc[i, 'destination']
            train_type = df_train_schedule_url.loc[i, 'train_type']
            train_schedule, duplicated_check_list = self.train_schedule_list(
                timetable_id, train_schedule_url, destination, train_type, duplicated_check_list, line_type)
            if train_schedule:
                train_schedule_list.extend(train_schedule)
                timetable_id += 1
                if line_type == 'circle':
                    break

        if not train_schedule_list:
            return None

        else:
            train_schedule_array = np.array(train_schedule_list)
            return train_schedule_array

    def destination_dict(self, destination_list):
        destination_dict = {}
        for ttl in destination_list:
            key = ttl.text.split('：')[0]
            value = ttl.text.split('：')[1]
            destination_dict[key] = value

        return destination_dict

    def train_type_dict(self, bs):
        train_type_list = bs.select('#timeNotice1 li')
        train_type_dict = {}
        for ttl in train_type_list:
            key = ttl.text.split('：')[0]
            value = ttl.text.split('：')[1]
            if key != '無印':
                train_type_dict[key] = value

        return train_type_dict

    def train_schedule_url(self, bs, destination_dict: dict, train_type_dict: dict):
        train_schedule_urls = []
        daytime = [i for i in range(8, 16)]
        for dt in daytime:
            timetable = bs.select(f'#hh_{dt} li')
            for tt in timetable:
                url = tt.find('a')['href']
                try:
                    destination = destination_dict[tt.select('dd.trainFor')[
                        0].text]
                except:
                    destination = destination_dict['無印']

                try:
                    train_type = train_type_dict[tt.select('dd.trainType')[
                        0].text[1:-1]]
                except:
                    train_type = '普通'

                train_schedule_urls.append(
                    [destination, train_type, 'https://transit.yahoo.co.jp/' + url])

        df_train_schedule_url = pd.DataFrame(
            train_schedule_urls, columns=['destination', 'train_type', 'url'])

        return df_train_schedule_url

    def train_schedule_list(self, index: int, url: str, destination: str, train_type: str, check_list: list, line_type: str):
        response = requests.get(url)
        bs = BeautifulSoup(response.text, 'html.parser')
        train_schedule = bs.select('#mdDiaStopSta > ul > li')
        first_station = train_schedule[0]('p')[0].text
        if line_type == 'circle':
            last_station = first_station
        else:
            last_station = train_schedule[-1]('p')[0].text

        station_length = len(train_schedule)
        check_word = f"{first_station}_{last_station}_{station_length}"
        if check_word in check_list:
            return None, check_list

        check_list.append(check_word)
        train_schedule_list = []
        for i, ts in enumerate(train_schedule):
            if i == 0:
                station1 = ts('p')[0].text
                estimated_time = int(ts('p')[1].text.split('分')[0])
                continue
            elif ts('p')[0].text == last_station:
                station2 = ts('p')[0].text
                train_schedule_list.append(
                    [index, destination, train_type, station1, station2, estimated_time])
                break
            else:
                station2 = ts('p')[0].text
                train_schedule_list.append(
                    [index, destination, train_type, station1, station2, estimated_time])
                station1 = station2
                estimated_time = int(ts('p')[1].text.split('分')[0])

        return train_schedule_list, check_list
