#!/usr/bin/env python
# coding: utf-8

import time
import numpy as np
import pandas as pd
from train_schedule import GetTrainSchedule

if __name__ == '__main__':
    unfound_train_schedule_urls = [
        {'line_code': '11311', 'line_name': 'JR中央本線',
         'url': 'https://transit.yahoo.co.jp/station/time/23408/?gid=1070&q=%E7%94%B2%E5%BA%9C&kind=1&done=time'},
        {'line_code': '11311', 'line_name': 'JR中央本線',
         'url': 'https://transit.yahoo.co.jp/station/time/24143/?gid=1071&kind=1&done=time'},
        {'line_code': '11311', 'line_name': 'JR中央本線',
         'url': 'https://transit.yahoo.co.jp/station/time/24254/?gid=1081&done=time&tab=time'},
        {'line_code': '21002', 'line_name': '東武伊勢崎線',
         'url': 'https://transit.yahoo.co.jp/station/time/22495/?gid=2661&q=%E6%B5%85%E8%8D%89&kind=1&done=time'},
        {'line_code': '21002', 'line_name': '東武伊勢崎線',
         'url': 'https://transit.yahoo.co.jp/station/time/22630/?gid=2661&kind=1&done=time'},
        {'line_code': '21003', 'line_name': '東武日光線',
         'url': 'https://transit.yahoo.co.jp/station/time/21799/?gid=2740&kind=1&done=time'},
        {'line_code': '21003', 'line_name': '東武日光線',
         'url': 'https://transit.yahoo.co.jp/station/time/22144/?gid=2741&kind=1&done=time'},
        {'line_code': '23001', 'line_name': '京成本線',
         'url': 'https://transit.yahoo.co.jp/station/time/22413/?gid=2960&kind=1&done=time'},
    ]

    train_schedule_column = ['line_station_info_id', 'line_name', 'line_code', 'timetable_id',
                             'destination', 'train_type', 'station1', 'station2', 'estimated_time']
    unfound_train_schedule = []
    train_schedule = np.empty((0, len(train_schedule_column)), int)
    print(f'total station line urls: {len(unfound_train_schedule_urls)}')

    for i in range(len(unfound_train_schedule_urls)):
        start = time.time()
        timetable_url = unfound_train_schedule_urls[i]['url']
        gts = GetTrainSchedule()

        if type(timetable_url) == str:
            line_code = unfound_train_schedule_urls[i]['line_code']
            line_name = unfound_train_schedule_urls[i]['line_name']
            line_type = None
            train_schedule_array = gts.train_schedule(timetable_url, line_type)

        if type(train_schedule_array) != np.ndarray:
            unfound_train_schedule.append(df_line_station_info.loc[i])
            print(f"{i+1}, Don't get train schedule in {line_name}.")
            continue

        else:
            line_array = np.full((train_schedule_array.shape[0], 3), [
                i+1, line_name, line_code])
            tmp = np.concatenate(
                (line_array, train_schedule_array), axis=1)
            train_schedule = np.vstack((train_schedule, tmp))
            elapsed_time = time.time() - start
            print(f"{i+1}, {line_name}, elapsed_time:{elapsed_time}[sec]")

    # Save train schedule
    train_schedule_path = '/home/vagrant/share/data/train_schedule/'
    df_train_schedule = pd.DataFrame(
        train_schedule, columns=train_schedule_column)
    df_train_schedule.to_csv(train_schedule_path +
                             'additional_train_schedule.csv', index=False)
    print("Done!")
