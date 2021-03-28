#!/usr/bin/env python
# coding: utf-8

import os
import time
import pickle
import argparse
import numpy as np
import pandas as pd
from train_schedule import GetTrainSchedule


if __name__ == '__main__':
    # Set argument
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--loadfile', default='line_station_info.csv', help='load csv file')
    parser.add_argument(
        '--picklefile', default='train_schedule.pkl', help='load and save pickle file')
    parser.add_argument(
        '--savefile', default='train_schedule.csv', help='save csv file')
    args = parser.parse_args()

    # Load line station info
    train_schedule_path = '/home/vagrant/share/data/train_schedule/'
    df_line_station_info = pd.read_csv(
        train_schedule_path + args.loadfile)

    # Get train schedule
    print(f'total station line urls: {df_line_station_info.shape[0]}')
    train_schedule_column = ['line_station_info_id', 'line_name', 'line_code', 'timetable_id',
                             'destination', 'train_type', 'station1', 'station2', 'estimated_time']
    unfound_train_schedule = []

    # Check if station line urls file exists
    train_schedule_pickle_path = train_schedule_path + args.pklfile
    if os.path.exists(train_schedule_pickle_path):
        with open(train_schedule_pickle_path, 'rb') as f:
            train_schedule = pickle.load(f)
        skip_flag = True

    else:
        train_schedule = np.empty((0, len(train_schedule_column)), int)
        skip_flag = False

    for i in df_line_station_info.index:
        if skip_flag:
            if i < int(train_schedule[-1][0]):
                continue
            else:
                skip_flag = False

        start = time.time()
        timetable_url = df_line_station_info.loc[i, 'timetable_url']
        gts = GetTrainSchedule()

        if type(timetable_url) == str:
            line_code = df_line_station_info.loc[i, 'line_code']
            line_name = df_line_station_info.loc[i, 'line_name']
            line_type = df_line_station_info.loc[i, 'line_type']
            train_schedule_array = gts.train_schedule(timetable_url, line_type)

        else:
            print("timetable_url is nan")
            print(f"{i+1}, {line_name}")
            continue

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

            if i % 3 == 0:
                with open(train_schedule_pickle_path, 'wb') as f:
                    pickle.dump(train_schedule, f)
                print("Save the results up to now")

    # Save train schedule
    with open(train_schedule_pickle_path, 'wb') as f:
        pickle.dump(train_schedule, f)

    df_train_schedule = pd.DataFrame(
        train_schedule, columns=train_schedule_column)
    df_train_schedule.to_csv(train_schedule_path +
                             args.savefile, index=False)

    # Save unfound_train_schedule
    if unfound_train_schedule:
        df_unfound_train_schedule = pd.DataFrame(unfound_train_schedule)
        df_unfound_train_schedule.to_csv(
            train_schedule_path + "unfound_train_schedule.csv", index=False)
    print('Done!')
