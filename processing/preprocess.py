#!/usr/bin/env python
# coding: utf-8

import time
import pandas as pd
from geopy import distance
from chardet.universaldetector import UniversalDetector


one_km_latitude = 0.0090133729745762
one_km_longitude = 0.010966404715491394


def cal_minmax_latlon(lat, lon, dist_range):
    min_lat = lat - one_km_latitude * dist_range
    max_lat = lat + one_km_latitude * dist_range
    min_lon = lon - one_km_longitude * dist_range
    max_lon = lon + one_km_longitude * dist_range
    return min_lat, max_lat, min_lon, max_lon


def select_by_mesh(df, lat, lon, dist_range):
    min_lat, max_lat, min_lon, max_lon = cal_minmax_latlon(
        lat, lon, dist_range)
    df = df[(df['lat'] > min_lat) & (df['lat'] < max_lat)]
    df = df[(df['lon'] > min_lon) & (df['lon'] < max_lon)]
    if df.shape[0]:
        for i in df.index:
            dist = distance.distance([lat, lon], df.loc[i, ['lat', 'lon']]).km
            if dist > dist_range:
                df.drop(i, inplace=True)
    return df


def select_by_pref_cd(pref_cd: list, df_station: pd.DataFrame, df_line=None, df_join=None, df_company=None) -> dict:
    delete_index = [i for i, pc in enumerate(
        df_station['pref_cd']) if pc not in pref_cd]
    df_tmp = df_station.drop(delete_index).reset_index(drop=True)
    line_cd = list(set(df_tmp['line_cd']))
    line_cd.sort()
    delete_index = [i for i, lc in enumerate(
        df_station['line_cd']) if lc not in line_cd]
    df_station = df_station.drop(delete_index).reset_index(drop=True)
    result = {'station': df_station}

    if type(df_line) == pd.DataFrame:
        delete_index = [i for i, lc in enumerate(
            df_line['line_cd']) if lc not in line_cd]
        df_line = df_line.drop(delete_index).reset_index(drop=True)
        result['line'] = df_line

    if type(df_join) == pd.DataFrame:
        delete_index = [i for i, lc in enumerate(
            df_join['line_cd']) if lc not in line_cd]
        df_join = df_join.drop(delete_index).reset_index(drop=True)
        result['join'] = df_join

    if type(df_company) == pd.DataFrame:
        company_cd = list(set(df_line['company_cd']))
        delete_index = [i for i, lc in enumerate(
            df_company['company_cd']) if lc not in company_cd]
        df_company = df_company.drop(delete_index).reset_index(drop=True)
        result['company'] = df_company

    return result


def create_conversion_dict(df: pd.DataFrame, tag: str, dict_type='code_to_name') -> dict:
    tag_list = ['station', 'line', 'company', 'pref']
    dict_type_list = ['code_to_name', 'name_to_code']
    if not tag in tag_list:
        raise ValueError(f'wrong tag values, please select from {tag_list}')

    if not dict_type in dict_type_list:
        raise ValueError(
            f'wrong dict_type values, please select from {dict_type_list}')

    if dict_type == 'code_to_name':
        code_to_name = {}
        for i in df.index:
            code_to_name[df[f'{tag}_cd'][i]] = df[f'{tag}_name'][i]

        return code_to_name

    elif dict_type == 'name_to_code':
        name_to_code = {}
        tag_set = list(set(df[f'{tag}_name']))
        for t in tag_set:
            name_to_code[t] = df[df[f'{tag}_name'] == t][f'{tag}_cd'].values

        return name_to_code


def get_pref_cd(df_pref: pd.DataFrame, df_station: pd.DataFrame, station_cd):
    if type(station_cd) == list:
        return [df_station[df_station['station_cd'] == sc]['pref_cd'].values[0] for sc in station_cd]
    pref_cd = df_station[df_station['station_cd']
                         == station_cd]['pref_cd'].values[0]
    return pref_cd


def get_first_and_last_pref_cd(df_pref: pd.DataFrame, df_station: pd.DataFrame, first_station_cd, last_station_cd):
    first_station_pref_cd = get_pref_cd(
        df_pref, df_station, first_station_cd)
    last_station_pref_cd = get_pref_cd(
        df_pref, df_station, last_station_cd)

    return first_station_pref_cd, last_station_pref_cd


def remove_bracket(text: str) -> str:
    bracket_patterns_front = ['(', '（', '〈']
    bracket_patterns_end = [')', '）', '〉']
    for bpf, bpe in zip(bracket_patterns_front, bracket_patterns_end):
        if text[0] == bpf:
            text = text.split(bpe)[1]
        elif text[-1] == bpe:
            text = text.split(bpf)[0]
        else:
            pass
    return text


def full_to_harf_width_char(text: str) -> str:
    return text.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))


def harf_to_full_width_char(text: str) -> str:
    return text.translate(str.maketrans({chr(0x0021 + i): chr(0xFF01 + i) for i in range(94)}))


def list_to_df(list: list, sort_col, drop_col):
    df = pd.DataFrame(list)
    df.sort_values(sort_col, inplace=True)
    df.drop_duplicates(drop_col, inplace=True)
    df = df.reset_index(drop=True)
    return df


def check_encoding(file_path):
    detector = UniversalDetector()
    with open(file_path, mode='rb') as f:
        for binary in f:
            detector.feed(binary)
            if detector.done:
                break
    detector.close()
    return detector.result['encoding']


def convert_point_to_latlon(df):
    df_tmp = pd.concat([df['geometry'].y, df['geometry'].x], axis=1)
    df_tmp.columns = ['lat', 'lon']
    df.drop(columns='geometry', inplace=True)
    df = pd.concat([df, df_tmp], axis=1)
    return df
