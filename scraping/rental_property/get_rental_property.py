#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
import json
import pickle
import datetime
import pandas as pd
from rental_property import *
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraping_utils import *  # nopep8


if __name__ == '__main__':
    rental_property_path = "/home/vagrant/share/data/rental_property/"
    area_urls_path = rental_property_path + 'area_urls.json'

    today = datetime.date.today()
    year_month = str(today.year) + str(today.month).zfill(2)
    save_path = rental_property_path + \
        f'rental_property_info_{year_month}.pkl'.format()

    if os.path.exists(area_urls_path):
        with open(area_urls_path, 'r') as f:
            area_urls = json.load(f)

    else:
        pref_path = '/home/vagrant/share/data/pref.csv'
        df_pref = pd.read_csv(pref_path)
        df_pref.set_index('id', inplace=True)
        use_id = [8, 9, 10, 19, 20, 22]
        df_pref = df_pref.loc[use_id]
        df_pref.set_index('romaji', inplace=True)
        pref_dict = df_pref['kanji'].to_dict()
        print("get area urls")
        area_urls = GetRentalProperty.area_urls(pref_dict)
        with open(area_urls_path, 'w') as f:
            json.dump(area_urls, f, indent=4, ensure_ascii=False)

    if os.path.exists(save_path):
        with open(save_path, 'rb') as f:
            property_list = pickle.load(f)
    else:
        property_list = []

    grp = GetRentalProperty()
    print("get rental protperty")
    for pref in area_urls.keys():
        print(f"{pref}, total municipality: {len(area_urls[pref])}")
        skip_set = set(t['municipality']
                       for t in property_list if t['prefectures'] == pref)
        i = 1
        for mun, url in area_urls[pref].items():
            if mun in skip_set:
                i += 1
                print(f"skip {mun}")
                continue

            page_id = 1
            start = time.time()

            while True:
                soup = get_soup(url + f"?page={page_id}")
                property_info = soup(class_="ui-frame-cacao-bar")
                if not property_info:
                    break
                for p in property_info:
                    try:
                        property_list = grp.property_info(
                            p, pref, mun, property_list)
                    except:
                        print(url + f"?page={page_id}",
                              p(class_='bukkenName')[0].text)
                page_id += 1

            with open(save_path, 'wb') as f:
                pickle.dump(property_list, f)
            elapsed_time = time.time() - start
            print(
                f"{i, pref, mun}, total pages:{page_id}, elapsed_time:{elapsed_time}[sec]")
            i += 1
        print('')
    print("Done!")
