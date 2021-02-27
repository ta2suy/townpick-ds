#!/usr/bin/env python
# coding: utf-8

import os
import time
import json
import pickle
import pandas as pd
from rent_market_price import GetAccessInfo, CreateRentMarketPrice


if __name__ == '__main__':
    # Load data
    rental_property_path = "/home/vagrant/share/data/rental_property/rental_property_info_202102.pickle"
    with open(rental_property_path, 'rb') as f:
        property_list = pickle.load(f)
    df_property = pd.DataFrame(property_list)

    data_path = "../../data/"
    station_property_dict_path = data_path + "station_property_dict.json"
    if os.path.exists(station_property_dict_path):
        with open(station_property_dict_path, 'r') as f:
            station_property_dict = json.load(f)
        print("load station_property_dict")
    else:
        station_name_dict_path = data_path + "station_name_dict.json"
        with open(station_name_dict_path, 'r') as f:
            station_name_dict = json.load(f)

        station_property_dict = {k: {} for k in station_name_dict.keys()}
        print("create station_property_dict")

        # Get access info
        print("Start to get access info")
        station_set = station_property_dict.keys()
        unfound_station_set = set()
        found_property_set = set()
        gai = GetAccessInfo(station_set, unfound_station_set)

        start = time.time()
        print(f"total property length: {df_property.shape[0]}")
        for i in df_property.index:
            pref = df_property.loc[i, 'prefectures']
            for a in df_property.loc[i, 'access']:
                access_info = gai.access_info(a, pref)
                if not access_info:
                    continue
                station = access_info[0]
                minutes_walk = access_info[1]
                found_property_set.add(i)

                if 'rental_property' in station_property_dict[station].keys():
                    station_property_dict[station]['rental_property'].append(
                        {"property_id": i, "minutes_walk": minutes_walk})
                else:
                    station_property_dict[station]['rental_property'] = [
                        {"property_id": i, "minutes_walk": minutes_walk}]

            if i % 10000 == 0:
                elapsed_time = time.time() - start
                print(f"{i}, elapsed_time:{elapsed_time}[sec]")
                start = time.time()

        # Save station_property_dict
        with open(station_property_dict_path, 'w') as f:
            json.dump(station_property_dict, f,
                      indent=4, ensure_ascii=False)

        print(
            f"unfound rental property: {df_property.shape[0] - len(found_property_set)}")

    # Create rent market price
    print("Start to create rent market price")
    # Load rent_market_price_dict if it exits
    rent_market_price_dict_path = data_path + "rent_market_price_dict.json"
    if os.path.exists(rent_market_price_dict_path):
        with open(rent_market_price_dict_path, 'r') as f:
            rent_market_price_dict = json.load(f)
        print("load rent_market_price_dict")
    else:
        rent_market_price_dict = {}

    station_list = [k for k, v in station_property_dict.items()
                    if 'rental_property' in v.keys() and not k in rent_market_price_dict.keys()]
    floor_plan_set = set()
    for unit in df_property['units']:
        for u in unit:
            floor_plan_set.add(u['floor_plan'])
    crmp = CreateRentMarketPrice(
        df_property, station_property_dict, floor_plan_set)
    property_type_index = crmp.select_by_property_type()
    year_built_index = crmp.select_by_year_built()
    print(f"total station length: {len(station_list)}")

    for i, s in enumerate(list(station_list)):
        start = time.time()
        print(i+1, s)
        tmp_dict = {}
        minutes_walk_index = crmp.select_by_minutes_walk(s)
        for pk, pv in property_type_index.items():
            for yk, yv in year_built_index.items():
                for mk, mv in minutes_walk_index.items():
                    units = df_property.loc[pv & yv & mv]['units'].values
                    if len(units) != 0:
                        if not pk in tmp_dict.keys():
                            tmp_dict[pk] = {}
                        if not yk in tmp_dict[pk].keys():
                            tmp_dict[pk][yk] = {}
                        if not mk in tmp_dict[pk][yk].keys():
                            tmp_dict[pk][yk][mk] = {}
                        tmp_dict[pk][yk][mk] = crmp.get_rent_price(
                            units)
        rent_market_price_dict[s] = tmp_dict
        elapsed_time = time.time() - start
        print(f"elapsed_time:{elapsed_time}[sec]")

        if i != 0 and i % 10 == 0:
            with open(rent_market_price_dict_path, 'w') as f:
                json.dump(rent_market_price_dict, f,
                          indent=4, ensure_ascii=False)
            print("Save dicts until now!")
            print()

    # Save rent_market_price_dicts
    with open(rent_market_price_dict_path, 'w') as f:
        json.dump(rent_market_price_dict, f, indent=4, ensure_ascii=False)
    print("Done!")
