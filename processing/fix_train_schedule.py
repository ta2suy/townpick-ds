#!/usr/bin/env python
# coding: utf-8

import os
import json
import time
import numpy as np
import pandas as pd
from preprocess import *


if __name__ == '__main__':
    # Load data
    train_schedule_path = '/home/vagrant/share/data/train_schedule/'
    train_schedule_fix_path = train_schedule_path + 'train_schedule_fix.csv'
    station_name_dict_path = '../data/station_name_dict.json'

    if os.path.exists(train_schedule_fix_path):
        df_train_schedule = pd.read_csv(
            train_schedule_fix_path)

    else:
        station_data_path = '/home/vagrant/share/data/station/'
        df_station = pd.read_csv(station_data_path + 'station20200619_fix.csv')

        df_train_schedule = pd.read_csv(
            train_schedule_path + 'train_schedule.csv')
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

    # Add additional fee columns in train schedule
    train_type_list = ['特急', '特急スカイライナー', ]

    exception_line_list = ['京王線', '京王高尾線', '京王相模原線', '京急本線',
                           '京急空港線', '京急久里浜線', '東急東横線', 'みなとみらい線', '相鉄本線']

    additional_fee = np.zeros(df_train_schedule.shape[0])
    for train_type in train_type_list:
        df_tmp = df_train_schedule[df_train_schedule['train_type'] == train_type]
        line_list = list(set(df_tmp['line_name']))

        # Remove exception line
        if train_type == '特急':
            line_list = [
                l for l in line_list if not l in exception_line_list]

        for l in line_list:
            i = df_tmp[df_tmp['line_name'] == l].index
            additional_fee[i] = 1

    df_additional_fee = pd.DataFrame(
        additional_fee, columns=['additional_fee']).astype('int')
    df_train_schedule = pd.concat(
        [df_train_schedule, df_additional_fee], axis=1)

    # Add station group code columns in train schedule
    if not 'station1_g_cd' in df_train_schedule.columns and os.path.exists(station_name_dict_path):
        with open(station_name_dict_path, 'r') as f:
            station_name_dict = json.load(f)

        station_g_cd_list = []
        for i in df_train_schedule.index:
            station1_g_cd = station_name_dict[df_train_schedule.loc[i,
                                                                    'station1']]['station_g_cd']
            station2_g_cd = station_name_dict[df_train_schedule.loc[i,
                                                                    'station2']]['station_g_cd']
            station_g_cd_list.append([station1_g_cd, station2_g_cd])

        df_station_g_cd = pd.DataFrame(station_g_cd_list, columns=[
            'station1_g_cd', 'station2_g_cd'])
        df_train_schedule = pd.concat(
            [df_train_schedule, df_station_g_cd], axis=1)

    # Save train schedule
    df_train_schedule.to_csv(train_schedule_fix_path, index=False)
