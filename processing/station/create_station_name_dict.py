#!/usr/bin/env python
# coding: utf-8

import os
import sys
import json
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
from preprocess import *  # nopep8


if __name__ == '__main__':
    # Load data
    station_data_path = '/home/vagrant/share/data/station/'
    df_station = pd.read_csv(station_data_path + 'station20200619_fix.csv')
    df_line = pd.read_csv(station_data_path + 'line20200619free.csv')
    df_pref = pd.read_csv(station_data_path + 'pref.csv')

    train_schedule_path = '/home/vagrant/share/data/train_schedule/'
    df_train_schedule = pd.read_csv(
        train_schedule_path + 'train_schedule_fix.csv')

    # Create conversion dict
    line_code_to_name = create_conversion_dict(df_line, tag='line')
    pref_cd_to_name = create_conversion_dict(df_pref, tag='pref')

    # Create station name dict
    all_station_list = list(
        get_station_set_in_train_schedule(df_train_schedule))
    all_station_list.sort()

    station_name_dict = {}
    for s in all_station_list:
        df_tmp = df_station[df_station['station_name'] == s]
        station_g_cd_list = list(set(df_tmp['station_g_cd'].values))
        line_cd_list = list(set(df_tmp['line_cd'].values))
        df_tmp = df_tmp.drop_duplicates('address')
        if len(station_g_cd_list) == 1:
            station_name_dict[s] = {
                'station_g_cd': int(station_g_cd_list[0]),
                'line': [line_code_to_name[lc] for lc in line_cd_list],
                'pref': pref_cd_to_name[df_tmp['pref_cd'].values[0]],
                'post': df_tmp['post'].values[0],
                'address': df_tmp['address'].values[0],
                'lat': df_tmp['lat'].values[0],
                'lon': df_tmp['lon'].values[0],
            }
        else:
            print(s)

    # Save station name dict
    station_name_dict_path = '../data/station_name_dict.json'
    with open(station_name_dict_path, 'w') as f:
        json.dump(station_name_dict, f, indent=4, ensure_ascii=False)
