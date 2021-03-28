#!/usr/bin/env python
# coding: utf-8

import re
import os
import sys
import datetime
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
from preprocess import remove_bracket  # nopep8


class CreateRentMarketPrice:
    def __init__(self, df: pd.DataFrame, station_property_dict: dict, floor_plan_set: set):
        self.df = df
        self.station_property_dict = station_property_dict
        self.this_year = datetime.date.today().year
        self.floor_plan_dict = {
            "1R~1DK": ['1R', '1K', '1SK', '1DK', '1SDK', '1LK', '1SLK'],
            "1LDK~2DK": ['1LDK', '1SLDK', '2K', '2SK', '2DK', '2SDK', '2LK', '2SLK'],
            "2LDK~3DK": ['2LDK', '2SLDK', '3K', '3SK', '3DK', '3SDK', '3LK', '3SLK'],
            "3LDK~4DK": ['3LDK', '3SLDK', '4K', '4SK', '4DK', '4SDK'],
            "4LDK~": list(floor_plan_set)
        }
        self.occupied_area_dict = {
            "x<=10㎡": 10,
            "10<x<=20㎡": 20,
            "20<x<=30㎡": 30,
            "30<x<=40㎡": 40,
            "40<x<=50㎡": 50,
            "50<x<=60㎡": 60,
            "60<x<=70㎡": 70,
            "70<x<=80㎡": 80,
            "80<x<=90㎡": 90,
            "90<x<=100㎡": 100,
            "100㎡<x": 10000
        }

    def select_by_property_type(self) -> dict:
        condominium = set(self.df[self.df['type'] == "マンション"].index)
        apartment = set(self.df[self.df['type'] == "アパート"].index)
        house = set(self.df[self.df['type'] == "一戸建て"].index)
        return {
            "condominium": condominium,
            "apartment": apartment,
            "house": house,
        }

    def select_by_year_built(self) -> dict:
        year_built = self.this_year - self.df['year_built'].values
        new_construction = set(
            self.df[year_built == 0].index)
        ten_or_less_year = set(
            self.df[(year_built > 0) & (year_built <= 10)].index)
        ten_twenty_year = set(
            self.df[(year_built > 10) & (year_built <= 20)].index)
        twenty_thirty_year = set(
            self.df[(year_built > 20) & (year_built <= 30)].index)
        thirty_fourty_year = set(
            self.df[(year_built > 30) & (year_built <= 40)].index)
        over_fourty_year = set(
            self.df[(year_built > 40)].index)
        return {
            "new": new_construction,
            "x<=10Y": ten_or_less_year,
            "10<x<=20Y": ten_twenty_year,
            "20<x<=30Y": twenty_thirty_year,
            "30<x<=40Y": thirty_fourty_year,
            "40Y<x": over_fourty_year,
        }

    def select_by_minutes_walk(self, station_name) -> dict:
        five_or_less_min = set()
        five_ten_min = set()
        ten_fifteen_min = set()
        fifteen_twenty_min = set()
        over_twenty_min = set()
        for rp in self.station_property_dict[station_name]['rental_property']:
            if rp['minutes_walk'] <= 5:
                five_or_less_min.add(rp['property_id'])
            elif rp['minutes_walk'] > 5 and rp['minutes_walk'] <= 10:
                five_ten_min.add(rp['property_id'])
            elif rp['minutes_walk'] > 10 and rp['minutes_walk'] <= 15:
                ten_fifteen_min.add(rp['property_id'])
            elif rp['minutes_walk'] > 15 and rp['minutes_walk'] <= 20:
                fifteen_twenty_min.add(rp['property_id'])
            elif rp['minutes_walk'] > 20:
                over_twenty_min.add(rp['property_id'])
            else:
                print(rp)
        return {
            "x<=5min": five_or_less_min,
            "5<x<=10min": five_ten_min,
            "10<x<=15min": ten_fifteen_min,
            "15<x<=20min": fifteen_twenty_min,
            "20min<x": over_twenty_min
        }

    def get_rent_price(self, units):
        unit_dict = {}
        for unit in units:
            for u in unit:
                for fpk, fpv in self.floor_plan_dict.items():
                    if u['floor_plan'] in fpv:
                        if not fpk in unit_dict.keys():
                            unit_dict[fpk] = {}
                        for oak, oav in self.occupied_area_dict.items():
                            if u['occupied_area'] <= oav:
                                if not oak in unit_dict[fpk].keys():
                                    unit_dict[fpk][oak] = {}
                                if not "total_price" in unit_dict[fpk][oak].keys():
                                    unit_dict[fpk][oak]['total_price'] = u['rent'] + \
                                        u['manegement_fee']
                                    unit_dict[fpk][oak]['num_units'] = 1
                                else:
                                    unit_dict[fpk][oak]['total_price'] += u['rent'] + \
                                        u['manegement_fee']
                                    unit_dict[fpk][oak]['num_units'] += 1
                                break
                        break
        for uk in unit_dict.keys():
            for k, v in unit_dict[uk].items():
                average_price = v['total_price'] / \
                    v['num_units']
                unit_dict[uk][k]['average_price'] = int(
                    round(average_price, -2))
        return unit_dict


class GetAccessInfo:
    def __init__(self, station_set, unfound_station_set):
        self.station_set = station_set
        self.unfound_station_set = unfound_station_set
        self.except_words_list = ["バス", "乗車", "号線", "IC", "インタ"]
        self.check_words_list = ["駅", "徒歩"]
        self.remove_first_char = ["・", "の"]
        self.remove_words = ["「", "」", "『", "』",
                             "(", ")", "\u3000", " ", "：", "/", "J"]
        self.remove_lines = ["R湘南新宿ライン宇須", "つくばエクスプレス", "ゆりかもめ", "北総鉄道",
                             "千葉都市モノレール", "埼玉高速鉄道", "日暮里舎人ライナー", "東京モノレール", "湘南新宿ライン", "金沢シーサイドライン"]
        self.station_dict = {
            '三郷(千葉県)': '三郷(埼玉県)',
            '平和台(埼玉県)': '平和台(千葉県)',
            '新町(埼玉県)': '新町(群馬県)',
            '東武霞ヶ関(埼玉県)': '霞ヶ関(埼玉県)',
            '三ッ沢上町(神奈川県)': '三ツ沢上町',
            '京成町屋(東京都)': '町屋',
            '浦安(東京都)': '浦安(千葉県)',
            '梅が丘(東京都)': '梅ヶ丘',
            '東京スカイツリー(東京都)': 'とうきょうスカイツリー',
            '町屋2丁目(東京都)': '町屋二丁目',
            '橋本(東京都)': '橋本(神奈川県)',
            '黒川(東京都)': '黒川(神奈川県)',
            'こどもの国(東京都)': 'こどもの国(神奈川県)',
        }

    def access_info(self, text: str, pref):
        text = self.check_words(text)
        if not text:
            return None
        text = text.replace("　", " ")
        access = text.split(" ")
        if len(access) == 3:
            station = remove_bracket(access[1])
            if station[-1] == '駅':
                station = station[:-1]
            if '徒歩' in access[2]:
                try:
                    minutes_walk = int(re.search("徒歩\d*", access[2])
                                       [0].replace("徒歩", ""))
                except:
                    print(f"Don't get minutes walk :{text}")
                    return None
            else:
                return None
        else:
            if text.count("駅") == 1:
                try:
                    minutes_walk = int(re.search("徒歩\d*", text)
                                       [0].replace("徒歩", ""))
                except:
                    print(f"Don't get minutes walk :{text}")
                    return None
                if text.count("線") == 0:
                    station = re.search(".*駅", text)[0][:-1]
                elif text.count("線") == 1:
                    station = re.search("線.*駅", text)[0][1:-1]
                else:
                    return None
            else:
                return None
        station = self.normalize_station(station)
        station = self.check_exception_station(station, access, pref)
        if not station:
            return None
        return station, minutes_walk

    def check_words(self, text: str):
        for ew in self.except_words_list:
            if ew in text:
                return None
        for cw in self.check_words_list:
            if not cw in text:
                return None
        return text

    def normalize_station(self, text: str) -> str:
        if text[0] in self.remove_first_char:
            text = text[1:]
        for rw in self.remove_words:
            text = text.replace(rw, '')
        for rl in self.remove_lines:
            text = text.replace(rl, '')
        return text.replace("ケ", "ヶ")

    def check_exception_station(self, station: str, access, pref):
        if not station in self.station_set:
            if station == '弘明寺':
                if access[0] == "横浜市営地下鉄ブルーライン":
                    station = station + "(横浜市営)"
                elif access[0] == "京急本線":
                    station = station + "(京急線)"
                else:
                    print(access[0], station)
            elif station == '早稲田':
                if access[0] == "東京メトロ東西線":
                    station = station + "(東京メトロ)"
                elif access[0] == "都電荒川線":
                    station = station + "(都電荒川線)"
                else:
                    print(access[0], station)
            else:
                station = station + "({})".format(pref)
                try:
                    station = self.station_dict[station]
                except:
                    pass
            if not station in self.station_set:
                self.unfound_station_set.add(station)
                return None
        return station
