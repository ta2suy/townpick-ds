#!/usr/bin/env python
# coding: utf-8

import time
import pickle
import numpy as np
import pandas as pd
from utils import GetTrainSchedule


if __name__ == '__main__':
    # Load line station info
    df_line_station_info = pd.read_csv('../../data/line_station_info.csv')

    # Get train schedule
    print(f'total station line urls: {df_line_station_info.shape[0]}')
    train_schedule = np.empty((0, 6), int)
    unfound_train_schedule = []

    for i in df_line_station_info.index:
        start = time.time()
        timetable_url = df_line_station_info.loc[i, 'timetable_url']
        last_station = df_line_station_info.loc[i, 'last_station']
        gts = GetTrainSchedule(last_station)

        if type(timetable_url) == str:
            line_code = df_line_station_info.loc[i, 'line_code']
            line_name = df_line_station_info.loc[i, 'line_name']
            train_schedule_array = gts.train_schedule(timetable_url)

        else:
            print("timetable_url is nan")
            print(f"{i+1}, {line_name}")
            continue

        if type(train_schedule_array) != np.ndarray:
            unfound_train_schedule.append(df_line_station_info.loc[i])
            print(f"{i+1}, Don't get train schedule in {line_name}.")
            continue

        else:
            line_array = np.full((train_schedule_array.shape[0], 2), [
                line_name, line_code])
            tmp = np.concatenate(
                (line_array, train_schedule_array), axis=1)
            train_schedule = np.vstack((train_schedule, tmp))

            elapsed_time = time.time() - start
            print(f"{i+1}, {line_name}, elapsed_time:{elapsed_time}[sec]")

    train_schedule_column = ['line_name', 'line_code',
                             'train_type', 'station1', 'station2', 'estimated_time']

    # Save train schedule
    df_train_schedule = pd.DataFrame(
        train_schedule, columns=train_schedule_column)
    df_train_schedule.to_csv('../../data/train_schedule.csv', index=False)

    # Save unfound_train_schedule
    if not unfound_train_schedule:
        df_unfound_train_schedule = pd.DataFrame(unfound_train_schedule)
        df_unfound_train_schedule.to_csv(
            "../../data/unfound_train_schedule.csv", index=False)
    print('Done!')
