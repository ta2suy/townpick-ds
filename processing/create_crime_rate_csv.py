#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
from tabula import read_pdf

if __name__ == '__main__':
    # Saitama
    print("create csv in saitama")
    df_list_saitama = read_pdf(
        "/home/vagrant/share/data/crime_rate/R2_saitama.pdf", pages='all')
    tmp = [int(t.split(' ')[0].replace(',', ''))
           for t in df_list_saitama[0].iloc[2:, 3].values]
    mun = df_list_saitama[1].iloc[1:, 0].values
    df_saitama = pd.DataFrame([mun, np.array(tmp)]).T
    df_saitama.columns = ["市区町村", "総数"]
    df_saitama.to_csv(
        "/home/vagrant/share/data/crime_rate/R2_saitama.csv", index=False)

    # Chiba
    print("create csv in chiba")
    df_list_chiba = read_pdf(
        "/home/vagrant/share/data/crime_rate/R2_chiba.pdf", pages='all')
    df_list_chiba[0].iloc[4:9, :-1] = df_list_chiba[0].iloc[4:9, 1:]
    df_list_chiba[0] = df_list_chiba[0].iloc[:, :-1]
    df_chiba = pd.concat([df_list_chiba[0], df_list_chiba[2].loc[2:]])

    index = [0, 1, 2, 8, 14, 28, 32, 35]
    columns = [
        "市区町村",
        "総数",
        '凶悪犯合計',
        '粗暴犯合計',
        '窃盗犯合計',
        '知能犯合計',
        '風俗犯合計',
        'その他刑法犯合計',
    ]

    df_chiba = df_chiba.iloc[2:, index]
    df_chiba.columns = columns
    df_chiba.reset_index(drop=True, inplace=True)
    for c in df_chiba.columns:
        try:
            for i in df_chiba.index:
                df_chiba.loc[i, c] = df_chiba.loc[i, c].replace(",", "")
            df_chiba[c] = df_chiba[c].astype(int)
        except:
            pass

    df_chiba.to_csv(
        "/home/vagrant/share/data/crime_rate/R2_chiba.csv", index=False)

    # Kanagawa
    print("create csv in kanagawa")
    df_list_kanagawa = read_pdf(
        "/home/vagrant/share/data/crime_rate/R2_kanagawa.pdf", pages='all')
    index = df_list_kanagawa[0][df_list_kanagawa[0].iloc[:, 0].isnull()].index
    df_list_kanagawa[0].iloc[index, :-1] = df_list_kanagawa[0].iloc[index, 1:]
    df_list_kanagawa[0].iloc[1:3, 1:] = df_list_kanagawa[0].iloc[1:3, :-1]
    df_list_kanagawa[0].iloc[2, 0] = "総数"
    index = [0, 1, 2, 6, 11, 14, 17]
    columns = [
        "市区町村",
        "総数",
        "凶悪犯合計",
        "粗暴犯合計",
        "知能犯合計",
        "風俗犯合計",
        "その他刑法犯合計",
    ]

    df_kanagawa = df_list_kanagawa[0].iloc[2:, index]
    df_kanagawa.columns = columns
    df_kanagawa.reset_index(drop=True, inplace=True)
    df_tmp = pd.DataFrame(
        df_list_kanagawa[2].iloc[2:, 2].values, columns=["窃盗犯合計"])
    df_kanagawa = pd.concat([df_kanagawa, df_tmp], axis=1)

    index = df_list_kanagawa[3][df_list_kanagawa[3].iloc[:, 0].isnull()].index
    df_list_kanagawa[3].iloc[index, :-1] = df_list_kanagawa[3].iloc[index, 1:]
    mun = df_list_kanagawa[3].iloc[2:, 0].values.reshape(-1, 1)
    index = [5, 6, 12, 18, 21, 24]
    tmp1 = df_list_kanagawa[1].iloc[4:, index].values
    tmp2 = tmp = df_list_kanagawa[3].iloc[2:, 1].values.reshape(-1, 1)
    df_tmp = pd.DataFrame(np.concatenate(
        [mun, tmp1, tmp2], axis=1), columns=df_kanagawa.columns)
    df_kanagawa = pd.concat([df_kanagawa, df_tmp], axis=0)
    df_kanagawa.reset_index(drop=True, inplace=True)

    for c in df_kanagawa.columns:
        try:
            df_kanagawa[c] = df_kanagawa[c].mask(df_kanagawa[c] == '-', 0)
            for i in df_kanagawa.index:
                df_kanagawa.loc[i, c] = df_kanagawa.loc[i, c].replace(",", "")
                df_kanagawa = df_kanagawa.astype(int)
        except:
            pass

    df_kanagawa = pd.concat(
        [df_kanagawa.iloc[:, :4], df_kanagawa.iloc[:, -1], df_kanagawa.iloc[:, 4:-1]], axis=1)
    df_kanagawa.to_csv(
        "/ home/vagrant/share/data/crime_rate/R2_kanagawa.csv", index=False)
