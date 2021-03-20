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
    CityParkCd = {
        1: '街区公園',
        2: '近隣公園',
        3: '地区公園（カントリーパーク）',
        4: '総合公園',
        5: '運動公園',
        6: '広域公園',
        7: 'レクリエーション都市',
        8: '国営公園',
        9: '特殊公園（風致公園、動植物公園、歴史公園、墓園）',
        10: '緩衝緑地',
        11: '都市緑地',
        12: '緑道',
        13: '都市林',
        14: '広場公園',
    }

    CityPlanningDecisionCd = {
        0: '未確認',
        1: '決定',
        2: '未決定'
    }

    df['公園種別'] = [CityParkCd[tmp] for tmp in df['公園種別'].values]
    df['都市計画決定'] = [CityPlanningDecisionCd[tmp] for tmp in df['都市計画決定'].values]

    return df


if __name__ == '__main__':
    print('load data')
    data_path = '/home/vagrant/share/data/city_park/*/*.shp'
    files = glob.glob(data_path)
    df_list = []
    for path in files:
        df_list.append(gpd.read_file(path, encoding="shift-jis"))

    df = pd.concat(df_list)
    df.reset_index(drop=True, inplace=True)
    print('convert point to latlon')
    df = convert_point_to_latlon(df)

    column_list = [
        '管理都道府県・整備局',
        '管理市区町村',
        '公園名',
        '公園種別',
        '所在地都道府県名',
        '所在地市区町村名',
        '供用開始年',
        '供用済面積（m2）',
        '都市計画決定',
        '備考',
        'lat',
        'lon'
    ]

    df.columns = column_list
    df = convert_index_to_name(df)

    df.to_csv('../../data/city_park.csv', index=False)
    print('Done!')
