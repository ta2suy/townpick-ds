#!/usr/bin/env python
# coding: utf-8

import json
import time
import numpy as np
import pandas as pd
from preprocess import *


if __name__ == '__main__':
    # Load data
    raw_station_data_path = '/home/vagrant/share/data/station/'
    df_station = pd.read_csv(raw_station_data_path + 'station20200619_fix.csv')
    df_line = pd.read_csv(raw_station_data_path + 'line20200619free.csv')
    df_join = pd.read_csv(raw_station_data_path + 'join20200619_fix.csv')
    df_company = pd.read_csv(raw_station_data_path + 'company20200619.csv')
    df_pref = pd.read_csv(raw_station_data_path + 'pref.csv')

    train_schedule_path = '../data/train_schedule/'
    df_linene_station_info = pd.read_csv(
        train_schedule_path + 'line_station_info.csv')
    df_train_schedule = pd.read_csv(train_schedule_path + 'train_schedule.csv')
    df_train_schedule_in_unfound = pd.read_csv(
        train_schedule_path + 'train_schedule_in_unfound.csv')
    df_additional_train_schedule = pd.read_csv(
        train_schedule_path + 'additional_train_schedule.csv')
    df_train_schedule = pd.concat(
        [df_train_schedule, df_train_schedule_in_unfound, df_additional_train_schedule]).reset_index(drop=False)

    # Normalize station name in train schedule
    print(f"total length: {df_train_schedule.shape[0]}")
    start = time.time()
    for i in df_train_schedule.index:
        df_train_schedule.loc[i, 'station1'] = full_to_harf_width_char(
            df_train_schedule.loc[i, 'station1']).replace('ケ', 'ヶ')
        df_train_schedule.loc[i, 'station2'] = full_to_harf_width_char(
            df_train_schedule.loc[i, 'station2']).replace('ケ', 'ヶ')
        if i % 1000 == 0 and i != 0:
            elapsed_time = time.time() - start
            print(f"{i}, elapsed_time:{elapsed_time}[sec]")
            start = time.time()

    # Change station name in train schedule
    change_station_name_list = [
        {'line_code': 29001, 'pre_station_name': '星川',
            'post_station_name': '星川(神奈川県)'},
        {'line_code': 29002, 'pre_station_name': '星川',
            'post_station_name': '星川(神奈川県)'},
        {'line_code': 22011, 'pre_station_name': '八坂',
            'post_station_name': '八坂(東京都)'},
        {'line_code': 21004, 'pre_station_name': '南桜井',
            'post_station_name': '南桜井(埼玉県)'},
    ]

    for station_name_dict in change_station_name_list:
        for c in ['station1', 'station2']:
            index = df_train_schedule.loc[(df_train_schedule[c] == station_name_dict['pre_station_name']) & (
                df_train_schedule['line_code'] == station_name_dict['line_code'])].index
            for i in index:
                df_train_schedule.loc[i,
                                      c] = station_name_dict['post_station_name']

    # Change station name in train schedule
    train_schedule_station_set = get_station_set_in_train_schedule(
        df_train_schedule)
    station_set = set(df_station['station_name'].values)
    all_station_set = train_schedule_station_set | station_set
    unfound_station_in_train_schedule = all_station_set ^ station_set

    change_station_name_dict = {}
    station_list = list(station_set)
    for us in list(unfound_station_in_train_schedule):
        for sl in station_list:
            #         if us in sl:
            #             print(f"station_set: {sl}, unfound_station: {us}")
            if remove_bracket(us) == sl:
                change_station_name_dict[us] = sl
                print(f"station_set: {sl}, unfound_station: {us}")

    for k, v in change_station_name_dict.items():
        for c in ['station1', 'station2']:
            index = df_train_schedule[df_train_schedule[c] == k].index
            for i in index:
                df_train_schedule.loc[i, c] = v

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

    # Add station group code in train schedule
    station_g_cd_list = []
    for i in df_train_schedule.index:
        station1_g_cd = station_name_dict[df_train_schedule.loc[i,
                                                                'station1']]['station_g_cd']
        station2_g_cd = station_name_dict[df_train_schedule.loc[i,
                                                                'station2']]['station_g_cd']
        station_g_cd_list.append([station1_g_cd, station2_g_cd])

    df_station_g_cd = pd.DataFrame(station_g_cd_list, columns=[
                                   'station1_g_cd', 'station2_g_cd'])
    df_train_schedule = pd.concat([df_train_schedule, df_station_g_cd], axis=1)
    df_train_schedule.to_csv(train_schedule_path +
                             'train_schedule_fix.csv', index=False)

    # Create station group code dict
    station_g_cd_set_list = list(
        set(v['station_g_cd'] for v in station_name_dict.values()))
    df_tmp1 = df_train_schedule[['line_name',
                                 'line_code', 'station1', 'station1_g_cd']]
    df_tmp2 = df_train_schedule[['line_name',
                                 'line_code', 'station2', 'station2_g_cd']]
    tmp_array = np.concatenate([df_tmp1.values, df_tmp2.values])
    df_train_schedule_set = pd.DataFrame(
        tmp_array, columns=['line_name', 'line_code', 'station_name', 'station_g_cd'])
    df_train_schedule_set.drop_duplicates(inplace=True)
    df_train_schedule_set = df_train_schedule_set.reset_index(drop=True)

    station_g_code_dict = {}
    for sgc in station_g_cd_set_list:
        df_tmp = df_train_schedule_set[df_train_schedule_set['station_g_cd'] == sgc]
        station_g_code_dict[sgc] = {
            'station': list(set(df_tmp['station_name'].values)),
            'line_name': df_tmp['line_name'].values.tolist(),
            'line_cd': df_tmp['line_code'].values.tolist(),
        }

    # Save station group code dict
    station_g_code_dict_path = '../data/station_g_cd_dict.json'
    with open(station_g_code_dict_path, 'w') as f:
        json.dump(station_g_code_dict, f, indent=4, ensure_ascii=False)
