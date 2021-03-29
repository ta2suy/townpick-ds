#!/usr/bin/env python
# coding: utf-8

import os
import sys
import glob
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from preprocess import remove_bracket  # nopep8


class CreateCensus:
    def __init__(self, use_pref):
        self.use_pref = use_pref
        self.census_path = "/home/vagrant/share/data/census/"

    def load_data(self):
        key_latlon_path = self.census_path + "key_latlon.csv"
        self.df_key_latlon = pd.read_csv(key_latlon_path)
        dir_paths = glob.glob(self.census_path + "2015/*")
        dir_paths.sort()
        all_data = []
        for p in dir_paths[:-1]:
            if p.split("/")[-1][:2] in self.use_pref:
                path = glob.glob(p+"/006_*")[0]
                print(path)
                try:
                    df = pd.read_csv(path, encoding="shift-jis")
                except:
                    df = pd.read_csv(path, encoding="CP932")
                df = df.iloc[:, 1:]
                columns = self.get_columns_from_census(df, 2, 3)
                df.columns = columns
                df = df.iloc[4:]
                all_data.append(df)

        df = pd.concat(all_data, axis=0)
        df.reset_index(drop=True, inplace=True)

        return df

    def get_columns_from_census(self, df, category_row, columns_row):
        columns = []
        columns_num = []
        for c in df.loc[category_row][df.loc[category_row].notnull()].index:
            columns_num.append(df.columns.get_loc(c))

        for i in range(len(columns_num)):
            if i == 0:
                columns.extend(df.iloc[columns_row, :columns_num[i]].values)
            else:
                tmp = df.iloc[columns_row, columns_num[i-1]
                    :columns_num[i]].values
                cotegory = remove_bracket(
                    df.iloc[category_row, columns_num[i-1]])
                columns.extend([cotegory+"_"+t for t in tmp])
            if i == len(columns_num)-1:
                tmp = df.iloc[columns_row, columns_num[i]:].values
                cotegory = remove_bracket(
                    df.iloc[category_row, columns_num[i]])
                columns.extend([cotegory+"_"+t for t in tmp])
        return columns

    def preprocess(self, df):
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
        return df

    def create_index(self, df):
        df = pd.merge(df, self.df_key_latlon, on='key_code', how='inner')
        df['single_rate'] = df['一般世帯数_単独世帯'] / df['一般世帯数_総数（世帯の家族類型）']
        df['dinks_rate'] = df['一般世帯人員_うち夫婦のみの世帯'] / df['一般世帯数_総数（世帯の家族類型）']
        df['0~5age_rate'] = df['６歳未満世帯員のいる一般世帯数_総数（世帯の家族類型）'] / \
            df['一般世帯数_総数（世帯の家族類型）']
        df['6~18age_rate'] = (df['18歳未満世帯員のいる一般世帯数_総数（世帯の家族類型）'] -
                        df['６歳未満世帯員のいる一般世帯数_総数（世帯の家族類型）']) / df['一般世帯数_総数（世帯の家族類型）']
        return df


if __name__ == '__main__':
    # Load data
    use_pref = ["08", "09", "10", "11", "12", "13", "14", "19", "20", "22"]
    cc = CreateCensus(use_pref)
    print("load data")
    df = cc.load_data()

    # Create census data
    print("preprocess data")
    df = cc.preprocess(df)
    print("create index")
    df = cc.create_index(df)

    # Save data
    save_path = "../../data/census.csv"
    df.to_csv(save_path, index=False)
    print("Done!")
