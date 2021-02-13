#!/usr/bin/env python
# coding: utf-8

import json
import time
import numpy as np
import pandas as pd
from utils import GetUrls


if __name__ == '__main__':
    # Load line station info
    line_station_info_path = '../../data/line_station_info.csv'
    df_line_station_info = pd.read_csv(line_station_info_path)

    if not 'timetable_url' in df_line_station_info.columns:
        df_line_station_info['timetable_url'] = None

        # Load change line name dict
        with open('../../data/change_line_name.json', 'r') as f:
            change_line_name_dict = json.load(f)

        # Get unfound urls
        df_unfound_urls = df_line_station_info[df_line_station_info['timetable_url'].isnull(
        )]

        # Get timetable by first station
        timetable_urls = []
        print(f'total station line urls: {df_unfound_urls.shape[0]}')
        for i in df_unfound_urls.index:
            url = df_unfound_urls.loc[i, 'station_line_url']
            line_name = df_unfound_urls.loc[i, 'line_name']
            last_station = df_unfound_urls.loc[i, 'last_station']
            print(i + 1, line_name, last_station)

            # Change line name in unfound urls data
            if line_name in change_line_name_dict.keys():
                line_name = change_line_name_dict[line_name]

            df_line_station_info.loc[i, 'timetable_url'] = GetUrls.timetable(
                url, line_name, last_station)

        df_line_station_info.to_csv(line_station_info_path, index=False)

    # Get unfound urls
    df_unfound_urls = df_line_station_info[df_line_station_info['timetable_url'].isnull(
    )]

    # Get timetable by last station in unfound urls
    print(f'total unfound urls: {df_unfound_urls.shape[0]}')
    for i in df_unfound_urls.index:
        start = time.time()
        first_station = df_unfound_urls.loc[i, 'first_station']
        last_station = df_unfound_urls.loc[i, 'last_station']
        last_station_pref = df_unfound_urls.loc[i, 'last_station_pref']
        tmp_station_line_url = GetUrls.station_line(
            last_station, last_station_pref)
        if tmp_station_line_url != None:
            line_name = df_unfound_urls.loc[i, 'line_name']
            tmp_timetable_url = GetUrls.timetable(
                tmp_station_line_url, line_name, last_station)
            if tmp_timetable_url != None:
                df_line_station_info.loc[i, 'last_station'] = first_station
                df_line_station_info.loc[i, 'first_station'] = last_station
                df_line_station_info.loc[i,
                                         'station_line_url'] = tmp_station_line_url
                df_line_station_info.loc[i,
                                         'timetable_url'] = tmp_timetable_url

        elapsed_time = time.time() - start
        print(
            f"{i}, {last_station}, elapsed_time:{elapsed_time}[sec]")

    df_line_station_info.to_csv(line_station_info_path, index=False)
    print('Done!')
