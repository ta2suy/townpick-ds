#!/usr/bin/env python
# coding: utf-8

import pandas as pd


def get_station_set_in_train_schedule(df_train_schedule: pd.DataFrame, tag='name') -> set:
    tag_list = ['name', 'code']
    if not tag in tag_list:
        raise ValueError(f'wrong tag values, please select from {tag_list}')

    if tag == 'name':
        station1 = set(df_train_schedule['station1'].values)
        station2 = set(df_train_schedule['station2'].values)
    elif tag == 'code':
        station1 = set(df_train_schedule['station1_g_cd'].values)
        station2 = set(df_train_schedule['station2_g_cd'].values)

    return station1 | station2
