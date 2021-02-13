#!/usr/bin/env python
# coding: utf-8

import pandas as pd

if __name__ == '__main__':
    # Load data
    df_join = pd.read_csv('~/share/data/station/join20200619.csv')
    df_station = pd.read_csv(
        '/home/vagrant/share/data/station/station20200619free.csv')

    # 99425:あいの風とやま鉄道線
    line_cd = 99425

    df_join_tmp = df_join[df_join['line_cd'] == line_cd]
    symmetric_difference_station_cd = set(
        df_join_tmp['station_cd1']) ^ set(df_join_tmp['station_cd2'])
    append_dict = {'line_cd': 99425,
                   'station_cd1': 1140509, 'station_cd2': 1140510}

    # Check if append_dict is inclued
    if append_dict['station_cd1'] in symmetric_difference_station_cd and append_dict['station_cd2'] in symmetric_difference_station_cd:
        print(
            f"symmetric_difference_station_cd: {symmetric_difference_station_cd}")
        df_join = df_join.append(append_dict, ignore_index=True)

    # Add 高輪ゲートウェイ between 田町 and 品川 in JR京浜東北線(11332)
    line_cd = 11332
    tamachi_cd = df_station[(df_station['line_cd'] == line_cd) & (
        df_station['station_name'] == '田町')]['station_cd'].values[0]
    takanawa_gw_cd = df_station[(df_station['line_cd'] == line_cd) & (
        df_station['station_name'] == '高輪ゲートウェイ')]['station_cd'].values[0]
    shinagawa_cd = df_station[(df_station['line_cd'] == line_cd) & (
        df_station['station_name'] == '品川')]['station_cd'].values[0]

    df_tmp = df_join[df_join['line_cd'] == line_cd]
    change_index = df_tmp[(df_tmp['station_cd1'] == tamachi_cd) & (
        df_tmp['station_cd2'] == shinagawa_cd)].index
    if not change_index.empty:
        print(f"change_index: {change_index}")
        df_join.loc[change_index, 'station_cd2'] = takanawa_gw_cd
        append_dict = {'line_cd': 11332,
                       'station_cd1': takanawa_gw_cd, 'station_cd2': shinagawa_cd}
        df_join = df_join.append(append_dict, ignore_index=True)

    df_join.to_csv(
        '~/share/data/station/join20200619_fix.csv', index=False)
