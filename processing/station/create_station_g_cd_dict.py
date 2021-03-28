#!/usr/bin/env python
# coding: utf-8

import os
import sys
import pickle
import numpy as np
import pandas as pd
from station import get_station_set_in_train_schedule  # nopep8


if __name__ == '__main__':
    # Load data
    train_schedule_path = '/home/vagrant/share/data/train_schedule/'
    df_train_schedule = pd.read_csv(
        train_schedule_path + 'train_schedule_fix.csv')

    # Remove limited express line
    df_train_schedule = df_train_schedule[df_train_schedule['additional_fee'] == 0].reset_index(
        drop=True)

    # Create station group code dict
    station_g_cd_set_list = list(
        get_station_set_in_train_schedule(df_train_schedule, 'code'))
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
    station_g_code_dict_path = '../data/station_g_cd_dict.pkl'
    with open(station_g_code_dict_path, 'wb') as f:
        pickle.dump(station_g_code_dict, f)
