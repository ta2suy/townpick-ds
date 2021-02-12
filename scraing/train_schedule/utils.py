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


def set_driver():
    # Set driver
    opt = Options()
    opt.add_argument('--headless')

    # Open browser
    driver = webdriver.Chrome(options=opt)

    return driver


class LineStationInfo:
    def __init__(self, company_code_to_name: dict, line_code_to_name: dict, station_code_to_name: dict, pref_code_to_name: dict, ):
        self.line_station_info = []
        self.company_code_to_name = company_code_to_name
        self.line_code_to_name = line_code_to_name
        self.station_code_to_name = station_code_to_name
        self.pref_code_to_name = pref_code_to_name

    def covert_code_to_name(self, code, code_to_name_dict: dict):
        if type(code) in [int, np.int64]:
            name = code_to_name_dict[code]

        else:
            print(type(code))
            raise TypeError("worng code type")

        return name

    def remove_bracket(self, text: str):
        bracket_patterns = ['(', '（', '〈']

        for bp in bracket_patterns:
            text = text.split(bp)[0]

        return text

    def add_station_info(self, company_cd, line_cd, line_type, first_station_cd, last_station_cd, first_station_pref_cd, last_station_pref_cd):

        company_name = self.covert_code_to_name(
            company_cd, self.company_code_to_name)
        line_name = self.covert_code_to_name(line_cd, self.line_code_to_name)
        first_station_name = self.covert_code_to_name(
            first_station_cd, self.station_code_to_name)
        last_station_name = self.covert_code_to_name(
            last_station_cd, self.station_code_to_name)
        first_station_pref = self.covert_code_to_name(
            first_station_pref_cd, self.pref_code_to_name)
        last_station_pref = self.covert_code_to_name(
            last_station_pref_cd, self.pref_code_to_name)

        # Remove '(xxx)'
        line_name = self.remove_bracket(line_name)
        first_station_name = self.remove_bracket(first_station_name)
        last_station_name = self.remove_bracket(last_station_name)

        # # Covert 'JR東日本' and 'JR東海' to 'JR'
        # if company_name == 'JR東日本' or company_name == 'JR東海':
        #     company_name = 'JR'

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
        # with open(path, 'wb') as f:
        #     pickle.dump(self.line_station_info, f)


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
        bs = BeautifulSoup(response.text, 'html.parser')
        links_in_line = bs(class_='elmSearchItem direction')[0]('dl')

        if 'JR' in line_name:
            line_name = line_name.replace('JR', 'ＪＲ')

        for ll in links_in_line:
            if line_name == ll('dt')[0].text:

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
    def __init__(self, last_station):
        self.driver = set_driver()
        self.last_station = last_station

    def train_schedule(self, timetable_url: str):
        self.driver.get(timetable_url)
        WebDriverWait(self.driver, 30).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "elmLineDia")))
        try:
            response = self.driver.find_element_by_class_name('elmLineDia')
        except:
            print('unfound url')
            return None

        bs = BeautifulSoup(
            response.get_attribute('innerHTML'), 'html.parser')
        destination_list = bs.select('#timeNotice2 li')

        train_type_dict = self.train_type_dict(bs)
        train_for = self.train_for(destination_list)

        df_train_schedule_url = self.train_schedule_url(
            bs, train_for, train_type_dict)
        if df_train_schedule_url.empty and train_for != '無印':
            print(f'Unfound train schedule in {train_for}')
            train_for = '無印'
            df_train_schedule_url = self.train_schedule_url(
                bs, train_for, train_type_dict)

        df_train_schedule_url.drop_duplicates('train_type', inplace=True)

        train_schedule_list = []
        for i in df_train_schedule_url.index:
            train_schedule_url = df_train_schedule_url.loc[i, 'url']
            train_type = df_train_schedule_url.loc[i, 'train_type']
            train_schedule_list.extend(self.train_schedule_list(
                train_schedule_url, train_type))

        if not train_schedule_list:
            return None

        else:
            train_schedule_array = np.array(train_schedule_list)
            return train_schedule_array

    def train_type_dict(self, bs):
        train_type_list = bs.select('#timeNotice1 li')
        train_type_dict = {}
        for ttl in train_type_list:
            key = ttl.text.split('：')[0]
            value = ttl.text.split('：')[1]
            if key != '無印':
                train_type_dict[key] = value
        return train_type_dict

    def train_for(self, destination_list):
        train_for = [dl.text.split('：')[0]
                     for dl in destination_list if self.last_station in dl.text]
        if len(train_for) == 0:
            print(f'unfound train_for')
            return '無印'
        elif len(train_for) == 1:
            train_for = train_for[0]
            return train_for
        else:
            print(f'train_for length is more than 2, train_for:{train_for}')
            return '無印'

    def train_schedule_url(self, bs, train_for, train_type_dict):
        train_schedule_urls = []
        daytime = [i for i in range(8, 17)]
        for dt in daytime:
            timetable = bs.select(f'#hh_{dt} li')
            for tt in timetable:
                if tt.select('dd.trainFor'):
                    if tt.select('dd.trainFor')[0].text == train_for:
                        url = tt.find('a')['href']
                        try:
                            train_type = train_type_dict[tt.select('dd.trainType')[
                                0].text[1:-1]]
                        except:
                            train_type = '普通'
                        train_schedule_urls.append(
                            [train_type, 'https://transit.yahoo.co.jp/' + url])

                elif not tt.select('dd.trainFor') and train_for == '無印':
                    url = tt.find('a')['href']
                    try:
                        train_type = train_type_dict[tt.select('dd.trainType')[
                            0].text[1:-1]]
                    except:
                        train_type = '普通'
                    train_schedule_urls.append(
                        [train_type, 'https://transit.yahoo.co.jp/' + url])
                else:
                    continue

        df_train_schedule_url = pd.DataFrame(
            train_schedule_urls, columns=['train_type', 'url'])

        return df_train_schedule_url

    def train_schedule_list(self, url: str, train_type: str):
        train_schedule_list = []
        response = requests.get(url)
        bs = BeautifulSoup(response.text, 'html.parser')
        train_schedule = bs.select('#mdDiaStopSta > ul > li')
        first_station = bs.select(
            '#main > div.mainWrp > div.labelLarge > h1')[0].text
        found_first_station_flag = False

        for ts in train_schedule:
            if found_first_station_flag:
                station2 = ts('p')[0].text
                train_schedule_list.append(
                    [train_type, station1, station2, estimated_time])
                if station2 == self.last_station:
                    break
                station1 = station2
                try:
                    estimated_time = int(ts('p')[1].text.split('分')[0])
                except:
                    break

            else:
                if ts('p')[0].text == first_station:
                    station1 = ts('p')[0].text
                    estimated_time = int(ts('p')[1].text.split('分')[0])
                    found_first_station_flag = True
                else:
                    continue

        return train_schedule_list
