#!/usr/bin/env python
# coding: utf-8

import glob
import numpy as np
import pandas as pd


def load_population():
    path = "/home/vagrant/share/data/crime_rate/2020-a.xls"
    df = pd.read_excel(path, skiprows=5)
    df = df[['Unnamed: 7', '市区町村', '総人口']]
    df.columns = ['code', '市区町村', '総人口']
    df.dropna(subset=["code"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['code'] = df['code'].astype(int).astype(str)
    mun = [df.loc[i, '市区町村'].replace(
        "\u3000", "").replace(" ", "") for i in df.index]
    df['市区町村'] = mun
    pref_path = '/home/vagrant/share/data/etc/pref.csv'
    df_pref = pd.read_csv(pref_path)
    pref_id_kanji_dict = {
        str(df_pref.loc[i, "id"]).zfill(2): df_pref.loc[i, "kanji"] for i in df_pref.index}

    for i in df.index:
        if len(df.loc[i, "code"]) > 3:
            df.loc[i, "code"] = df.loc[i, "code"].zfill(5)
        else:
            df.loc[i, "code"] = df.loc[i, "code"].zfill(2)

    pref_list = [8, 9, 10, 11, 12, 13, 14, 19, 20, 22]
    tmp = []
    for p in pref_list:
        p_code = str(p).zfill(2)
        for i in df.index:
            if len(df.loc[i, "code"]) > 3:
                if df.loc[i, "code"][:len(p_code)] == p_code:
                    tmp.append([df.loc[i, "code"], pref_id_kanji_dict[p_code],
                                df.loc[i, '市区町村'].replace("ケ", "ヶ"), df.loc[i, '総人口']])
    df_population = pd.DataFrame(tmp, columns=["code", "都道府県", "市区町村", "総人口"])

    tokyo_index = []
    for i in df.index:
        if df.loc[i, "code"][:2] == "13":
            tokyo_index.append(i)
    df_tokyo = df.loc[tokyo_index].reset_index(drop=True)
    return df_population, df_tokyo


def summarize_tokyo(df, df_tokyo):
    tokyo_dict = {}
    for mun in df_tokyo["市区町村"].values:
        df_tmp = df[df["市区町丁"] == mun+"計"]['総合計']
        if df_tmp.shape[0] > 0:
            tokyo_dict[mun] = df_tmp.values[0]
        else:
            df_tmp = df.loc[[i for i in df.index if mun in df.loc[i, "市区町丁"]]]
            if df_tmp.shape[0] > 0:
                tokyo_dict[mun] = sum(df_tmp['総合計'])
    df = pd.DataFrame([tokyo_dict]).T
    df.reset_index(inplace=True)
    df.insert(0, "都道府県", "東京都")
    return df


if __name__ == "__main__":
    df_population, df_tokyo = load_population()
    crime_rate_path = "/home/vagrant/share/data/crime_rate/csv/*.csv"
    csv_files = glob.glob(crime_rate_path)
    array = np.empty((0, 3))
    for path in csv_files:
        if "tokyo" in path:
            df = pd.read_csv(path, encoding="shift-jis")
            df = summarize_tokyo(df, df_tokyo)
        else:
            df = pd.read_csv(path)
            df = df[["都道府県", "市区町村", "刑法犯総数"]]
        array = np.vstack((array, df.values))
    df_crime_rate = pd.DataFrame(array, columns=["都道府県", "市区町村", "刑法犯総数"])
    df_crime_rate = pd.merge(df_population, df_crime_rate, how="right")
    df_crime_rate['犯罪率(件/1000人)'] = df_crime_rate['刑法犯総数'] / \
        df_crime_rate['総人口'] * 1000
    df_crime_rate.to_csv("../../data/crime_rate.csv")
