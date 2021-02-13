#!/usr/bin/env python
# coding: utf-8

import pickle
import numpy as np
import pandas as pd
from preprocess import *
from utils import LineStationInfo


if __name__ == '__main__':
    # Load dataset
    print('Load dataset')
    df_station = pd.read_csv('~/share/data/station/station20200619free.csv')
    df_line = pd.read_csv('~/share/data/station/line20200619free.csv')
    df_join = pd.read_csv('~/share/data/station/join20200619_fix.csv')
    df_company = pd.read_csv('~/share/data/station/company20200619.csv')
    df_pref = pd.read_csv('~/share/data/station/pref.csv')

    # Select saitama, chiba, tokyo and kanagawa data
    pref_cd = [11, 12, 13, 14]
    df_all_dict = select_by_pref_cd(
        pref_cd, df_station, df_line, df_join, df_company)
    df_station = df_all_dict['station']
    df_line = df_all_dict['line']
    df_join = df_all_dict['join']
    df_company = df_all_dict['company']

    # Create conversion dictionaries
    company_code_to_name = create_conversion_dict(df_company, tag='company')
    line_code_to_name = create_conversion_dict(df_line, tag='line')
    station_code_to_name = create_conversion_dict(df_station, tag='station')
    pref_code_to_name = create_conversion_dict(df_pref, tag='pref')

    # Create LineStationInfo instance
    lsi = LineStationInfo(company_code_to_name,
                          line_code_to_name, station_code_to_name, pref_code_to_name)

    # Determine first & last station code to dict for each line type
    print('Determine first & last station code to dict for each line type')
    check_station_cd_list = []
    line_station_info = {}

    for line_cd in df_line['line_cd'].values:
        company_cd = df_line[df_line['line_cd']
                             == line_cd]['company_cd'].values[0]
        df_join_tmp = df_join[df_join['line_cd'] == line_cd]
        df_station_tmp = df_station[df_station['line_cd'] == line_cd]

        # Do not exist station or Duplicated line (99809:伊予鉄道環状線)
        if df_station_tmp.shape[0] == 0 or line_cd == 99809:
            continue
        symmetric_difference_station_cd = set(
            df_join_tmp['station_cd1']) ^ set(df_join_tmp['station_cd2'])

        # Circle type
        if len(symmetric_difference_station_cd) == 0:
            line_type = 'cricle'
            first_station_cd = df_station_tmp['station_cd'].values[0]
            last_station_cd = df_station_tmp['station_cd'].values[-1]

        # Line circle type
        elif len(symmetric_difference_station_cd) == 1:
            line_type = 'line_cricle'
            first_station_cd = list(symmetric_difference_station_cd)[0]
            if df_join_tmp[df_join_tmp['station_cd1'].duplicated()].shape[0] != 0:
                last_station_cd = df_join_tmp[df_join_tmp['station_cd1'].duplicated(
                )]['station_cd1'].values[0]
            else:
                last_station_cd = df_join_tmp[df_join_tmp['station_cd2'].duplicated(
                )]['station_cd2'].values[0]

        # Straight type
        elif len(symmetric_difference_station_cd) == 2:
            line_type = 'straight'
            first_station_cd = min(symmetric_difference_station_cd)
            last_station_cd = max(symmetric_difference_station_cd)

        # Branch type
        elif len(symmetric_difference_station_cd) == 3:
            line_type = 'branch'
            symmetric_difference_station_cd_list = list(
                symmetric_difference_station_cd)
            symmetric_difference_station_cd_list.sort()
            first_station_cd = symmetric_difference_station_cd_list[0]
            last_station_cd = symmetric_difference_station_cd_list[1:]

        # Etc type
        else:
            check_station_cd_list.append(line_cd)
            print('etc', line_cd,
                  line_code_to_name[line_cd], symmetric_difference_station_cd)
            continue

        # Add station info
        if type(last_station_cd) in [int, np.int64]:
            # Get first and last pref cd
            first_station_pref_cd, last_station_pref_cd = get_first_and_last_pref_cd(
                df_pref, df_station, first_station_cd, last_station_cd)

            lsi.add_station_info(company_cd, line_cd, line_type,
                                 first_station_cd, last_station_cd, first_station_pref_cd, last_station_pref_cd)

        elif type(last_station_cd) == list:
            last_station_cd_list = last_station_cd
            for last_station_cd in last_station_cd_list:
                # Get first and last pref cd
                first_station_pref_cd, last_station_pref_cd = get_first_and_last_pref_cd(
                    df_pref, df_station, first_station_cd, last_station_cd)

                lsi.add_station_info(company_cd, line_cd, line_type,
                                     first_station_cd, last_station_cd, first_station_pref_cd, last_station_pref_cd)

        else:
            print(
                f'wrong last station type, type is {type(last_station_cd)}')

    # Add station info in etc line type
    line_type = 'etc'

    for line_cd in check_station_cd_list:
        company_cd = df_line[df_line['line_cd']
                             == line_cd]['company_cd'].values[0]

        if line_cd == 11304:  # JR鶴見線
            first_station_cd = 1130401
            last_station_cd_list = [1130407, 1130409, 1130413]

            for last_station_cd in last_station_cd_list:
                # Get first and last pref cd
                first_station_pref_cd, last_station_pref_cd = get_first_and_last_pref_cd(
                    df_pref, df_station, first_station_cd, last_station_cd)
                lsi.add_station_info(company_cd, line_cd, line_type,
                                     first_station_cd, last_station_cd, first_station_pref_cd, last_station_pref_cd)

        elif line_cd == 11327:  # JR成田線
            first_station_cd_list = [1132701, 1132720]
            last_station_cd_list = [1132705, 1132719]

            for first_station_cd, last_station_cd in zip(first_station_cd_list, last_station_cd_list):
                # Get first and last pref cd
                first_station_pref_cd, last_station_pref_cd = get_first_and_last_pref_cd(
                    df_pref, df_station, first_station_cd, last_station_cd)
                lsi.add_station_info(company_cd, line_cd, line_type,
                                     first_station_cd, last_station_cd, first_station_pref_cd, last_station_pref_cd)

        elif line_cd == 11328:  # JR成田エクスプレス
            first_station_cd_list = [1132801, 1132804, 1132815]
            last_station_cd = 1132814

            for first_station_cd in first_station_cd_list:
                # Get first and last pref cd
                first_station_pref_cd, last_station_pref_cd = get_first_and_last_pref_cd(
                    df_pref, df_station, first_station_cd, last_station_cd)

                lsi.add_station_info(company_cd, line_cd, line_type,
                                     first_station_cd, last_station_cd, first_station_pref_cd, last_station_pref_cd)

        else:
            print(f'except line is {line_cd}')

    # Save line station info
    lsi.save_info('../../data/line_station_info.csv')
    print('Done!')
