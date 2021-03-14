#!/usr/bin/env python
# coding: utf-8

import os
import time
import pickle
import argparse
import numpy as np
import pandas as pd
from train_schedule import GetUrls


if __name__ == '__main__':
    # Set argument
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--csvfile', default='line_station_info.csv', help='load and save csv file')
    parser.add_argument(
        '--picklefile', default='station_line_urls.pickle', help='load and save pickle file')
    args = parser.parse_args()

    # Load line station info
    train_schedule_path = '/home/vagrant/share/data/train_schedule/'
    line_station_info_path = train_schedule_path + args.csvfile
    df_line_station_info = pd.read_csv(line_station_info_path)

    if not 'station_line_url' in df_line_station_info.columns:
        df_line_station_info['station_line_url'] = None

    # Select first station set
    first_station_array = df_line_station_info[[
        'first_station', 'first_station_pref']].drop_duplicates().values

    # Check if station line urls file exists
    station_line_urls_path = train_schedule_path + args.picklefile
    if os.path.exists(station_line_urls_path):
        with open(station_line_urls_path, 'rb') as f:
            station_line_urls = pickle.load(f)

    # Get station urls
    else:
        print(
            f'start getting station urls, total station length:{len(first_station_array)}')
        station_line_urls = []
        i = 0

        for first_station, first_station_pref in first_station_array:
            i += 1
            start = time.time()
            url = GetUrls.station_line(first_station, first_station_pref)
            station_line_urls.append(url)

            elapsed_time = time.time() - start
            print(
                f"{i}, {first_station}, elapsed_time:{elapsed_time}[sec]")

        with open(station_line_urls_path, 'wb') as f:
            pickle.dump(station_line_urls, f)
        print('Saved station_line_urls with pickel')

    first_station_array = np.concatenate(
        (first_station_array, np.array(station_line_urls).reshape(-1, 1)), axis=1)
    df_station_line_urls = pd.DataFrame(
        first_station_array, columns=['station', 'pref', 'url'])

    for i in df_station_line_urls.index:
        station = df_station_line_urls.loc[i, 'station']
        pref = df_station_line_urls.loc[i, 'pref']
        url = df_station_line_urls.loc[i, 'url']
        df_line_station_info.loc[(df_line_station_info['first_station'] == station) & (
            df_line_station_info['first_station_pref'] == pref), 'station_line_url'] = url

    # Complement link in unfound station
    unfound_station_urls = [
        {'station': '新線新宿', 'line': '京王新線',
            'url': '/station/rail/22741/?q=%E6%96%B0%E5%AE%BF&kind=1'},
        {'station': '金沢八景', 'line': '京急逗子線',
            'url': '/station/rail/23113/?q=%E9%87%91%E6%B2%A2%E5%85%AB%E6%99%AF&kind=1&done=time'},
    ]

    for usu in unfound_station_urls:
        df_line_station_info.loc[(df_line_station_info['first_station'] == usu['station']) & (
            df_line_station_info['line_name'] == usu['line']), 'station_line_url'] = 'https://transit.yahoo.co.jp' + usu['url']

    # Save station urls
    df_line_station_info.to_csv(line_station_info_path, index=False)
    print('Done!')
