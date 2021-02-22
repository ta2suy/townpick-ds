#!/usr/bin/env python
# coding: utf-8

from preprocess import *
import pandas as pd
import argparse
import pickle
import time
import copy


def extract_stations_within_time(df_train_schedule: pd.DataFrame, line_code: int, station_code: int, accum_time: int, max_time: int, num_transfer: int, extracted_station_list: list) -> list:
    df_line_tmp = df_train_schedule[df_train_schedule['line_code'] == line_code]
    station1_timetable_id = set(
        df_line_tmp[df_line_tmp['station1_g_cd'] == station_code]['timetable_id'].values)
    station2_timetable_id = set(
        df_line_tmp[df_line_tmp['station2_g_cd'] == station_code]['timetable_id'].values)
    timetable_id_list = list(station1_timetable_id | station2_timetable_id)
    for ti in timetable_id_list:
        df_timetable_tmp = df_line_tmp[df_line_tmp['timetable_id'] == ti].reset_index(
            drop=True)

        index = df_timetable_tmp[df_timetable_tmp['station1_g_cd']
                                 == station_code].index
        if len(index) != 0:
            tmp_time = accum_time
            for i in range(index[0], df_timetable_tmp.shape[0]):
                tmp_time += df_timetable_tmp.loc[i, 'estimated_time']
                if tmp_time > max_time:
                    break
                extracted_station_list.append({
                    'station_g_cd': df_timetable_tmp.loc[i, 'station2_g_cd'],
                    'time_required': tmp_time,
                    'number_of_transfers': num_transfer,
                    'line_used': df_timetable_tmp.loc[i, 'line_name'],
                    'transfer_station': station_code,
                })

        index = df_timetable_tmp[df_timetable_tmp['station2_g_cd']
                                 == station_code].index
        if len(index) != 0:
            tmp_time = accum_time
            for i in reversed(range(0, index[0]+1)):
                tmp_time += df_timetable_tmp.loc[i, 'estimated_time']
                if tmp_time > max_time:
                    break
                extracted_station_list.append({
                    'station_g_cd': df_timetable_tmp.loc[i, 'station1_g_cd'],
                    'time_required': tmp_time,
                    'number_of_transfers': 0,
                    'line_used': df_timetable_tmp.loc[i, 'line_name'],
                    'transfer_station': station_code,
                })

    return extracted_station_list


if __name__ == '__main__':
    # Set argument
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--max_time', default=100, type=int, help='max time required')
    parser.add_argument(
        '--max_transfer', default=5, type=int, help='max number of transfer')
    args = parser.parse_args()

    # Load data
    train_schedule_path = '/home/vagrant/share/data/train_schedule/'
    df_train_schedule = pd.read_csv(
        train_schedule_path + 'train_schedule_fix.csv')

    with open('../data/station_g_cd_dict.pickle', 'rb') as f:
        station_g_code_dict = pickle.load(f)

    # Remove limited express line
    df_train_schedule = df_train_schedule[df_train_schedule['additional_fee'] == 0].reset_index(
        drop=True)

    # Extract stations within time required
    extracted_stations_dict = {}
    count_num = 0
    print(f"total station length: {len(station_g_code_dict)}")

    for sgc, scd in station_g_code_dict.items():
        count_num += 1
        start = time.time()
        extracted_stations_list = []
        accum_time = 0
        num_transfer = 0
        line_cd_list = copy.copy(scd['line_cd'])

        # Extract stations　without transfer
        for lc in line_cd_list:
            extracted_stations_list = extract_stations_within_time(
                df_train_schedule, lc, sgc, accum_time, args.max_time, num_transfer, extracted_stations_list)

        df_tmp = list_to_df(extracted_stations_list, sort_col=[
                            'time_required', 'number_of_transfers'], drop_col='station_g_cd')
        loop_flag = True
        num_transfer += 1

        # Extract stations with one or more transfers
        while(loop_flag):
            if num_transfer > args.max_transfer:
                break

            tmp_list = []
            for i in df_tmp.index:
                tmp_sgc = df_tmp.loc[i, 'station_g_cd']
                accum_time = df_tmp.loc[i, 'time_required']
                for lc in station_g_code_dict[tmp_sgc]['line_cd']:
                    if lc in line_cd_list:
                        continue
                    else:
                        line_cd_list.append(lc)
                        tmp_list = extract_stations_within_time(
                            df_train_schedule, lc, tmp_sgc, accum_time, args.max_time, num_transfer, tmp_list)

            if len(tmp_list) == 0:
                loop_flag = False
            else:
                df_tmp = list_to_df(tmp_list, sort_col=[
                                    'time_required', 'number_of_transfers'], drop_col='station_g_cd')
                extracted_stations_list.extend(tmp_list)
                num_transfer += 1

        df_tmp = list_to_df(extracted_stations_list, sort_col=[
                            'time_required', 'number_of_transfers'], drop_col='station_g_cd')
        extracted_stations_dict[sgc] = df_tmp.to_dict(orient='records')

        elapsed_time = time.time() - start
        print(
            f"{count_num}, {sgc, scd['station']}, elapsed_time:{elapsed_time}[sec]")

    # Save extracted stations
    with open('../data/extracted_stations_dict.pickle', 'wb') as f:
        pickle.dump(extracted_stations_dict, f)
    print("Done!")
