#!/usr/bin/env python
# coding: utf-8

import os
import sys
import glob
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocess import remove_bracket, check_encoding  # nopep8


def create_census(path: str):
    try:
        df = pd.read_csv(path, encoding="shift-jis")
    except:
        char_code = check_encoding(path)
        df = pd.read_csv(path, encoding=char_code)
    df = df.iloc[:, 1:]
    columns = get_columns_from_census(df, 2, 3)
    df.columns = columns
    df = df.iloc[4:]
    df['地域識別番号'] = df['地域識別番号'].astype(int)
    df = df[df['地域識別番号'] != 1]
    remove_mark = ['X', '-']
    for rm in remove_mark:
        df = df[df['一般世帯数_総数（世帯の家族類型）'] != rm]

    town_set = set(df[df['地域識別番号'] == 3]['市区町村名'] +
                   df[df['地域識別番号'] == 3]['大字・町名'])
    delete_index = []
    for i in df[df['地域識別番号'] == 2]['大字・町名'].index:
        if type(df.loc[i, '大字・町名']) != str:
            delete_index.append(i)
        elif df.loc[i, '市区町村名']+df.loc[i, '大字・町名'] in town_set:
            delete_index.append(i)

    df.drop(delete_index, inplace=True)
    df.reset_index(drop=True, inplace=True)

    df['key_code'] = df['市区町村コード']+df['町丁字コード']

    return df


def get_columns_from_census(df, category_row, columns_row):
    columns = []
    columns_num = []
    for c in df.loc[category_row][df.loc[category_row].notnull()].index:
        columns_num.append(df.columns.get_loc(c))

    for i in range(len(columns_num)):
        if i == 0:
            columns.extend(df.iloc[columns_row, :columns_num[i]].values)
        else:
            tmp = df.iloc[columns_row, columns_num[i-1]:columns_num[i]].values
            cotegory = remove_bracket(df.iloc[category_row, columns_num[i-1]])
            columns.extend([cotegory+"_"+t for t in tmp])
        if i == len(columns_num)-1:
            tmp = df.iloc[columns_row, columns_num[i]:].values
            cotegory = remove_bracket(df.iloc[category_row, columns_num[i]])
            columns.extend([cotegory+"_"+t for t in tmp])
    return columns


if __name__ == '__main__':
    # Load data
    key_latlon_path = "/home/vagrant/share/data/census/key_latlon.csv"
    df_key_latlon = pd.read_csv(key_latlon_path)

    census_path = "/home/vagrant/share/data/census/2015/*"
    file_paths = glob.glob(census_path)
    file_paths.sort()
    all_data = []

    # Create census data
    for p in file_paths[:-1]:
        path = glob.glob(p+"/006_*")[0]
        print(path)
        all_data.append(create_census(path))

    df = pd.concat(all_data, axis=0)
    df.reset_index(drop=True, inplace=True)
    df['key_code'] = df['key_code'].astype(int)

    for c in df.columns:
        df[c] = df[c].mask(df[c] == '-', 0)
        try:
            df[c] = df[c].astype(int)
        except:
            try:
                df[c] = df[c].astype(float)
            except:
                pass

    # create index
    df = pd.merge(df, df_key_latlon, on='key_code', how='inner')
    single_rate = df['一般世帯数_単独世帯'] / df['一般世帯数_総数（世帯の家族類型）']
    less_than_6age_rate = df['６歳未満世帯員のいる一般世帯数_総数（世帯の家族類型）'] / \
        df['一般世帯数_総数（世帯の家族類型）']
    less_than_18age_rate = df['18歳未満世帯員のいる一般世帯数_総数（世帯の家族類型）'] / \
        df['一般世帯数_総数（世帯の家族類型）']

    df['single_rate'] = single_rate
    df['less_than_6age_rate'] = less_than_6age_rate
    df['less_than_18age_rate'] = less_than_18age_rate

    # Save data
    save_path = "../../data/census.csv"
    df.to_csv(save_path, index=False)
    print("Done!")
