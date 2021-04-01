#!/usr/bin/env python
# coding: utf-8

import os
import copy
import json
import pickle
import shutil
import datetime
import numpy as np
import pandas as pd
from scipy.stats import rankdata
from sklearn.preprocessing import MinMaxScaler


class CalculateScore:
    def __init__(self):
        self.data_path = "../data/"

    def load_data(self):
        self.df = pd.read_csv(self.data_path +
                              "station_area_info_1km.csv", index_col=0)
        self.df.dropna(subset=["crime_rate"], inplace=True)
        self.station_set = set(self.df.index)
        with open(self.data_path + "rent_market_price.json", "r") as f:
            self.rent_market_price = json.load(f)
        with open(self.data_path + "weight_dict.json", "r") as f:
            weight_dict = json.load(f)
        with open(self.data_path + "property_conditions.json", "r") as f:
            conditions = json.load(f)
        return weight_dict, conditions

    def search_rent_market_price(self, condition):
        selected_rent_market_price = {}
        for sk, sv in self.rent_market_price.items():
            if not sk in self.station_set:
                continue
            total_price = []
            for pk, pv in sv.items():
                if not pk in condition["property_type"]:
                    continue
                for yk, yv in pv.items():
                    if not yk in condition["year"]:
                        continue
                    for mk, mv in yv.items():
                        if not mk in condition["minutes_walk"]:
                            continue
                        for fpk, fpv in mv.items():
                            if not fpk in condition["floor_plan"]:
                                continue
                            for fak, fav in fpv.items():
                                if not fak in condition["floor_area"]:
                                    continue
                                total_price.append(fav["average_price"])
            if total_price:
                selected_rent_market_price[sk] = round(
                    int(np.mean(total_price)), -3)
        return selected_rent_market_price

    def create_score(self, df, weight_dict, commute_type, distination):
        total_score = 0
        all_cols = []
        for key1, val1 in weight_dict.items():
            key1_cols = []
            if commute_type != None and key1 in ["cost", "transport"]:
                val1 = val1[commute_type]
            for key2, val2 in val1.items():
                key2_cols = []
                if type(val2) == dict:
                    for key3, val3 in val2.items():
                        df[f"{key3}_score"] = self.calculate_score(
                            df, key3, val3)
                        key2_cols.append(f"{key3}_score")
                    df = self.sum_cols(df, key2, key2_cols)
                    key1_cols.extend(key2_cols)
                else:
                    if key2 in ["time", "transfer"]:
                        key2 += f"_{distination}"
                    df[f"{key2}_score"] = self.calculate_score(
                        df, key2, val2)
                    key1_cols.append(f"{key2}_score")
            df = self.sum_cols(df, key1, key1_cols)
            all_cols.extend(key1_cols)
        df = self.sum_cols(df, "total", all_cols)
        df.sort_values("total_score", ascending=False, inplace=True)
        df.insert(0, "ranking", rankdata(df["total_score"]*-1, method="min"))
        df["ranking"] = df["ranking"].astype(int)
        return df

    def calculate_score(self, df, col, rate):
        score = copy.deepcopy(df[col].values)
        if col == "crime_rate" or col == "rent_market_price" or "time" in col or "transfer" in col:
            score *= -1
        score = MinMaxScaler().fit_transform(score.reshape(-1, 1))
        score *= rate
        score = np.round(score, 2)
        return score

    def sum_cols(self, df, key, cols):
        if len(cols) == 1:
            df.insert(0, f"{key}_score", df[cols])
        else:
            df.insert(0, f"{key}_score", round(
                df[cols].sum(axis=1), 2))
        return df

    def main(self, condition, weight_dict, commute_type=None, distination=None):
        rent_market_price = self.search_rent_market_price(condition)
        df = copy.deepcopy(self.df.loc[rent_market_price.keys()])
        df["rent_market_price"] = rent_market_price.values()
        return self.create_score(df, weight_dict, commute_type, distination)


if __name__ == "__main__":
    cs = CalculateScore()
    print("load data")
    weight_dict, conditions = cs.load_data()
    print("calculate score")
    station_list = ["tokyo", "shinagawa", "shinjuku", "shibuya", "ikebukuro"]
    result_path = "/home/vagrant/share/result/" + \
        datetime.datetime.now().strftime('%Y.%m.%d_%H.%M.%S') + "/"
    os.mkdir(result_path)
    for wdk, wdv in weight_dict.items():
        for k, v in conditions[wdk].items():
            print(wdk, k)
            if wdk == "family":
                df_score = cs.main(v, wdv)
            else:
                if k == "commute":
                    for station in station_list:
                        df_score = cs.main(v, wdv, k, station)
                        df_score.to_csv(
                            result_path + f"{wdk}_{k}_{station}_score.csv")
                    continue
                else:
                    df_score = cs.main(v, wdv, k)
            df_score.to_csv(result_path + f"{wdk}_{k}_score.csv")
    files = ["property_conditions.json", "weight_dict.json"]
    for f in files:
        shutil.copyfile(cs.data_path + f, result_path + f)
    print("Done")
