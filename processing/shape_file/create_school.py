#!/usr/bin/env python
# coding: utf-8

import os
import sys
import glob
import pandas as pd
import geopandas as gpd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocess import convert_point_to_latlon  # nopep8


def convert_index_to_name(df):
    SchoolClassCd = {
        16001: '小学校',
        16002: '中学校',
        16003: '中等教育学校',
        16004: '高等学校',
        16005: '高等専門学校',
        16006: '短期大学',
        16007: '大学',
        16012: '特別支援学校'
    }

    df['学校分類'] = [SchoolClassCd[tmp] for tmp in df['学校分類'].values]
    return df


if __name__ == '__main__':
    print('load data')
    data_path = '/home/vagrant/share/data/school/*/*.shp'
    files = glob.glob(data_path)
    df_list = []
    for path in files:
        df_list.append(gpd.read_file(path, encoding="shift-jis"))

    df = pd.concat(df_list)
    df.reset_index(drop=True, inplace=True)
    print('convert point to latlon')
    df = convert_point_to_latlon(df)

    column_list = [
        '行政区域コード',
        '公共施設大分類',
        '公共施設小分類',
        '学校分類',
        '名称',
        '所在地',
        '管理者コード',
        'lat',
        'lon'
    ]

    df.columns = column_list
    df['学校分類'] = df['学校分類'].astype(int)
    df = convert_index_to_name(df)

    df.to_csv('../../data/school.csv', index=False)
    print('Done!')
