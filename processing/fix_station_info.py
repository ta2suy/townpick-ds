#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
from preprocess import create_conversion_dict, normalize


if __name__ == '__main__':
    # Load dataset
    df_station = pd.read_csv('~/share/data/station/station20200619free.csv')
    df_pref = pd.read_csv('~/share/data/station/pref.csv')

    # Add みなみ寄居 station
    minami_yorii_info = {
        'station_cd': 2100139,
        'station_g_cd': 2100138,
        'station_name': 'みなみ寄居',
        'station_name_k': np.nan,
        'station_name_r': np.nan,
        'line_cd': 21001,
        'pref_cd': 11,
        'post': '369-1216',
        'address': '大里郡寄居町大字富田字橋ノ入南谷997-14',
        'lon': 139.2365,
        'lat': 36.092417,
        'open_ymd': '2020-10-31',
        'close_ymd': '0000-00-00',
        'e_status': 0,
        'e_sort': 2100139,
    }
    df_station = df_station.append(minami_yorii_info, ignore_index=True)

    # Normalize station name
    print("Start to normalize station name")
    pref_code_to_name = create_conversion_dict(df_pref, tag='pref')
    for i in df_station.index:
        df_station.loc[i, 'station_name'] = normalize(
            df_station.loc[i, 'station_name'])

    # Rename 新線新宿 to 新宿
    shinsen_shinjuku_id = df_station[df_station['station_name']
                                     == '新線新宿'].index
    df_station.loc[shinsen_shinjuku_id, 'station_name'] = '新宿'

    # Drop duplicated data in station name
    df_drop_duplicates = df_station.drop_duplicates(
        ['station_name', 'pref_cd'])
    df_duplicate = df_drop_duplicates[df_drop_duplicates.duplicated(
        ['station_name'], keep=False)]

    # Change duplicated station name
    print("Start to change duplicated station name")
    station_set = list(set(df_duplicate['station_name']))
    for ss in station_set:
        df_tmp = df_duplicate[df_duplicate['station_name'] == ss]
        for i in df_tmp.index:
            pref_name = pref_code_to_name[df_station.loc[i, 'pref_cd']]
            df_station.loc[i,
                           'station_name'] = f"{df_station.loc[i, 'station_name']}({pref_name})"
            print(df_station.loc[i, 'station_name'])

    # Change stations with the same name that cannot be transfered
    change_station_name_list = [
        {'station_g_cd': 2800404, 'station_name': '早稲田(東京メトロ)'},
        {'station_g_cd': 9930530, 'station_name': '早稲田(都電荒川線)'},
        {'station_g_cd': 1122932, 'station_name': '泉(常磐線)'},
        {'station_g_cd': 9921505, 'station_name': '泉(福島交通線)'},
        {'station_g_cd': 9930903, 'station_name': '浅草(TX)'},
        {'station_g_cd': 1141433, 'station_name': '下島(飯田線)'},
        {'station_g_cd': 9940711, 'station_name': '下島(松本電鉄線)'},
        {'station_g_cd': 2700132, 'station_name': '弘明寺(京急線)'},
        {'station_g_cd': 9931621, 'station_name': '弘明寺(横浜市営)'},
        {'station_g_cd': 1122201, 'station_name': '仙台(地下鉄)'},
    ]

    for d in change_station_name_list:
        df_station.loc[df_station['station_g_cd'] ==
                       d['station_g_cd'], 'station_name'] = d['station_name']

    # Save new station dataframe
    save_path = "~/share/data/station/station20200619_fix.csv"
    df_station.to_csv(save_path, index=False)
    print("Done!")
