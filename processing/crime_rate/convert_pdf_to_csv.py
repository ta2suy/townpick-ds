#!/usr/bin/env python
# coding: utf-8

import glob
import numpy as np
import pandas as pd
from tabula import read_pdf


def preprocess(df):
    for i in df.index:
        df.loc[i, "市区町村"] = df.loc[i, "市区町村"].replace(
            " ", "").replace("ケ", "ヶ")
        if "市" in df.loc[i, "市区町村"] and "区" in df.loc[i, "市区町村"]:
            df.loc[i, "市区町村"] = df.loc[i, "市区町村"].split("市")[-1]
        elif "郡" in df.loc[i, "市区町村"]:
            df.loc[i, "市区町村"] = df.loc[i, "市区町村"].split("郡")[-1]
    if df["刑法犯総数"].dtype == object:
        for i in df.index:
            df.loc[i, "刑法犯総数"] = df.loc[i, "刑法犯総数"].replace(",", "")
        df['刑法犯総数'] = df['刑法犯総数'].astype(int)
    return df


def saitama(df_list):
    df = df_list[0].iloc[3:-1, :4]
    for i in df.index:
        df.loc[i, '全刑法犯'] = df.loc[i, '全刑法犯'].split(' ')[0]
        if type(df.loc[i, 'Unnamed: 1']) == str:
            df.loc[i, 'Unnamed: 0'] = df.loc[i, 'Unnamed: 0'] + \
                df.loc[i, 'Unnamed: 1'].replace(" ", "")
    df = df[['Unnamed: 0', '全刑法犯']]
    df.columns = ["市区町村", "刑法犯総数"]
    return df


def chiba(df_list):
    df_list[0].iloc[4:9, :-1] = df_list[0].iloc[4:9, 1:]
    df_list[0] = df_list[0].iloc[:, :-1]
    df = pd.concat([df_list[0], df_list[2].loc[2:]])
    index = [0, 1, 2, 8, 14, 28, 32, 35]
    df = df.iloc[3:-2, :2]
    df.columns = ["市区町村", "刑法犯総数"]
    df.reset_index(drop=True, inplace=True)
    return df


def kanagawa(df_list):
    df1 = df_list[0].iloc[3:, :3]
    df1.reset_index(drop=True, inplace=True)
    for i in df1[df1.iloc[:, 0].notnull()].index:
        df1.iloc[i, 2] = df1.iloc[i, 1]
        df1.iloc[i, 1] = df1.iloc[i, 0]
    df1 = df1.iloc[:, 1:]
    df1.columns = ['市区町村', '刑法犯総数']
    df2 = df_list[1].iloc[4:-1, :6]
    df2.reset_index(drop=True, inplace=True)
    mun_list = []
    for i in df2.index:
        mun = ""
        for ci in range(5):
            if type(df2.iloc[i, ci]) == str:
                mun += df2.iloc[i, ci]
        mun_list.append(mun)

    df2.iloc[:, -1]
    df2 = pd.DataFrame([mun_list, df2.iloc[:, -1]]).T
    df2.columns = ['市区町村', '刑法犯総数']
    df = pd.concat([df1, df2], axis=0)
    df.reset_index(drop=True, inplace=True)
    delete_index = []
    for i in df.index:
        if df.loc[i, "市区町村"][-1] == "郡":
            delete_index.append(i)
    df.drop(delete_index, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def ibaraki(df_list):
    df = df_list[0].iloc[5:-1, :]
    df.dropna(subset=['刑 法'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    mun_list = []
    for i in df.index:
        mun = ""
        for ci in range(4):
            if type(df.iloc[i, ci]) == str:
                mun += df.iloc[i, ci]
        mun = mun.replace(" ", "")
        if "郡" in mun:
            mun = mun.split("郡")[-1]
        mun_list.append(mun)
    df = df[["刑 法", "Unnamed: 8"]]
    df.index = mun_list
    df.reset_index(inplace=True)
    df.columns = ["市区町村", "刑法犯総数", "1,000人当たり犯罪率"]
    for i in df.index:
        df.loc[i, '1,000人当たり犯罪率'] = df.loc[i, '1,000人当たり犯罪率'].split(' ')[
            0]
    df['1,000人当たり犯罪率'] = df['1,000人当たり犯罪率'].astype(float)
    return df


def gunma(df_list):
    df = df_list[0].iloc[1:-2, :3]
    df.drop(columns=['Unnamed: 0'], inplace=True)
    df.columns = ['市区町村', '刑法犯総数']
    df.dropna(subset=['刑法犯総数'], inplace=True)
    for i in df.index:
        df.loc[i, '刑法犯総数'] = df.loc[i, '刑法犯総数'].split(' ')[-1]
    idx = df[df['市区町村'] == "中 渋川市"].index
    df.loc[idx, '市区町村'] = "渋川市"
    return df


def yamanashi(df_list):
    df = df_list[0].iloc[:-1, [0, -1]]
    df.columns = ["市区町村", "刑法犯総数"]
    return df


def nagano(df_list):
    df = df_list[0].iloc[2:-1, :5]
    df.dropna(subset=["全刑法犯"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.iloc[73:, 1:5] = df.iloc[73:, 0:4]
    df = df[['全刑法犯', 'Unnamed: 1']]
    df.columns = ["市区町村", "刑法犯総数"]
    df["刑法犯総数"] = df["刑法犯総数"].mask(df["刑法犯総数"] == "-", "0")
    return df


def shizuoka(df_list):
    df = df_list[0].iloc[3:-1, :2]
    df.columns = ["市区町村", "刑法犯総数"]
    return df


if __name__ == '__main__':
    load_path = "/home/vagrant/share/data/crime_rate/pdf/*.pdf"
    save_path = "/home/vagrant/share/data/crime_rate/csv/"
    files = glob.glob(load_path)
    pref_path = '/home/vagrant/share/data/etc/pref.csv'
    df_pref = pd.read_csv(pref_path)
    pref_kanji_dict = {df_pref.loc[i, "romaji"]                       : df_pref.loc[i, "kanji"] for i in df_pref.index}
    pref_function_dict = {
        # "saitama": saitama,
        # "chiba": chiba,
        # "kanagawa": kanagawa,
        # "ibaraki": ibaraki,
        "gunma": gunma,
        # "yamanashi": yamanashi,
        # "nagano": nagano,
        # "shizuoka": shizuoka,
    }
    for path in files:
        for k, v in pref_function_dict.items():
            if k in path:
                print(f"create csv in {k}")
                df_list = read_pdf(path, pages='all')
                df = v(df_list)
                df.insert(0, "都道府県", pref_kanji_dict[k])
                df = preprocess(df)
                df.to_csv(save_path + path.split('/')
                          [-1].replace('pdf', 'csv'), index=False)
                continue
