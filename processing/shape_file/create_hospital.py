#!/usr/bin/env python
# coding: utf-8

import os
import sys
import glob
import pandas as pd
import geopandas as gpd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocess import convert_point_to_latlon  # nopep8


def create_medical_subjects(df):
    medical_subjects = []
    medical_subjects_columns = ['P04_004', 'P04_005', 'P04_006']
    for i in df.index:
        tmp = []
        for v in df.loc[i, medical_subjects_columns].values:
            if v == None:
                break
            else:
                tmp.extend(v.split('\u3000'))
        medical_subjects.append(tmp)
    df.insert(3, '診療科目', medical_subjects)
    df.drop(columns=medical_subjects_columns, inplace=True)
    return df


def convert_index_to_name(df):
    MedicalInstitutionCd = {
        '1': '病院',
        '2': '診療所',
        '3': '歯科診療所'
    }

    MedicalInstitutionOrganizationCd = {
        '1': '国',  # 厚生労働省､独立行政法人国立病院機構、国立大学法人､独立行政法人労働者健康福祉機構､国立高度専門医療研究センター、その他（国の機関）
        '2': '公的医療機関',  # 都道府県、市町村、地方独立行政法人、日赤、済生会、北海道社会事業協会、厚生連、国民健康保険団体連合会
        '3': '社会保険関係団体',  # 全国社会保険協会連合会、厚生年金事業振興団、船員保険会、健康保険組合及びその連合会、共済組合及びその連合会、国民健康保険組合
        '4': '医療法人',  # 医療法人
        '5': '個人',  # 個人
        '6': 'その他',  # 公益法人、私立学校法人、社会福祉法人、医療生協、会社、その他の法人
        '9': '分類対象外',  # 上記以外および診療所、歯科診療所
    }

    df['医療機関分類'] = [MedicalInstitutionCd[tmp] for tmp in df['医療機関分類'].values]
    df['開設者分類'] = [MedicalInstitutionOrganizationCd[tmp]
                   for tmp in df['開設者分類'].values]
    return df


if __name__ == '__main__':
    print('load data')
    data_path = '/home/vagrant/share/data/hospital/*/*.shp'
    files = glob.glob(data_path)
    df_list = []
    for path in files:
        df_list.append(gpd.read_file(path, encoding="shift-jis"))

    df = pd.concat(df_list)
    df.reset_index(drop=True, inplace=True)
    print('create medical subjects')
    df = create_medical_subjects(df)
    print('convert point to latlon')
    df = convert_point_to_latlon(df)
    column_list = [
        '医療機関分類',
        '施設名称',
        '所在地',
        '診療科目',
        '開設者分類',
        'lat',
        'lon'
    ]
    df.columns = column_list
    df = convert_index_to_name(df)

    df.to_csv('../../data/hospital.csv', index=False)
    print('Done!')
