#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from preprocess import *

if __name__ == '__main__':
    # Load data
    raw_station_data_path = '/home/vagrant/share/data/station/'
    train_schedule_path = '../../data/train_schedule/'
    df_station = pd.read_csv(raw_station_data_path + 'station20200619free.csv')
    df_line = pd.read_csv(raw_station_data_path + 'line20200619free.csv')
    df_join = pd.read_csv(raw_station_data_path + 'join20200619_fix.csv')
    df_company = pd.read_csv(raw_station_data_path + 'company20200619.csv')
    df_pref = pd.read_csv(raw_station_data_path + 'pref.csv')
    df_linene_station_info = pd.read_csv(
        train_schedule_path + 'line_station_info.csv')
    df_train_schedule = pd.read_csv(train_schedule_path + 'train_schedule.csv')

    # Select by pref
    pref_cd = [11, 12, 13, 14]
    df_all_dict = select_by_pref_cd(
        pref_cd, df_station, df_line, df_join, df_company)
    df_station = df_all_dict['station']
    df_line = df_all_dict['line']
    df_join = df_all_dict['join']
    df_company = df_all_dict['company']

    # Create conversion dict
    line_code_to_name = create_conversion_dict(df_line, tag='line')
    station_code_to_name = create_conversion_dict(df_station, tag='station')
    station_name_to_code = {v: k for k, v in station_code_to_name.items()}

    # Create line code list
    line_cd_list = list(set(df_train_schedule['line_code']))
    line_cd_list.sort()

    # Normalize station name
    df_join['station_cd1'] = [
        normalize(station_code_to_name[st1]) for st1 in df_join['station_cd1'].values]
    df_join['station_cd2'] = [
        normalize(station_code_to_name[st2]) for st2 in df_join['station_cd2'].values]
    df_train_schedule['station1'] = [
        normalize(st1) for st1 in df_train_schedule['station1'].values]
    df_train_schedule['station2'] = [
        normalize(st2) for st2 in df_train_schedule['station2'].values]

    print(f"total number of liens: {len(line_cd_list)}")

    # Get unfound line code
    unfound_line_cd = []
    for lc in line_cd_list:
        df_join_tmp = df_join[df_join['line_cd'] == lc]
        df_train_schedule_tmp = df_train_schedule[df_train_schedule['line_code'] == lc]
        join_station_set = set(df_join_tmp['station_cd1']) | set(
            df_join_tmp['station_cd2'])
        train_schedule_station_set = set(df_train_schedule_tmp['station1']) | set(
            df_train_schedule_tmp['station2'])

        all_station_set = train_schedule_station_set | join_station_set
        unfound_station_in_join = all_station_set ^ train_schedule_station_set
        unfound_station_in_train_schedule = all_station_set ^ join_station_set

        if unfound_station_in_join:
            unfound_line_cd.append(lc)
            print(lc, line_code_to_name[lc])
            print(f"unfound_station_in_join: {unfound_station_in_join}")
    #         print(f"unfound_station_in_train_schedule: {unfound_station_in_train_schedule}")
    #         print(df_join_tmp)
    #         print("")

    print(f"total line number of unfound station: {len(unfound_line_cd)}")

    # Create unfound line station info
    unfound_index = [
        i for i in df_linene_station_info.index if df_linene_station_info.loc[i, "line_code"] in unfound_line_cd]
    df_tmp = df_linene_station_info.loc[unfound_index]

    delete_list = [
        {'line_code': 11303, 'first_station': '川崎', 'last_station': '立川'},
        {'line_code': 23001, 'first_station': '京成上野', 'last_station': '成田空港'},
        {'line_code': 11327, 'first_station': '佐倉', 'last_station': '成田空港'}
    ]
    delete_index = []
    for dd in delete_list:
        delete_index.append(df_tmp[(df_tmp['line_code'] == dd['line_code']) & (
            df_tmp['first_station'] == dd['first_station']) & (df_tmp['last_station'] == dd['last_station'])].index.values[0])

    df_tmp.drop(delete_index, inplace=True)
    delete_columns = ['station_line_url', 'timetable_url']
    df_tmp.drop(columns=delete_columns, inplace=True)

    # Reindex columns
    reindex_columns = ['company_name', 'company_code', 'line_name', 'line_code', 'line_type',
                       'last_station', 'first_station', 'last_station_pref',
                       'first_station_pref']
    df_tmp = df_tmp.reindex(columns=reindex_columns)

    # Rename columns
    rename_columns = {
        'last_station': 'first_station',
        'first_station': 'last_station',
        'last_station_pref': 'first_station_pref',
        'first_station_pref': 'last_station_pref'
    }
    df_unfound_line_station_info = df_tmp.rename(columns=rename_columns)

    # Save unfound line station info
    df_unfound_line_station_info.to_csv(
        train_schedule_path + 'unfound_line_station_info.csv', index=False)
    print("Done!")
