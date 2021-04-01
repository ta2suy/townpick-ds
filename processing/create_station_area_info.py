#!/usr/bin/env python
# coding: utf-8

import sys
import time
import json
import glob
import pickle
import argparse
import numpy as np
import pandas as pd
from preprocess import select_by_mesh


class CreateStationAreaInfo:
    def __init__(self, dist_range):
        self.dist_range = dist_range
        self.data_path = "../data/"
        self.raw_data_path = "/home/vagrant/share/data/"
        self.terminal_station = {
            "東京": "tokyo",
            "品川": "shinagawa",
            "新宿": "shinjuku",
            "渋谷": "shibuya",
            "池袋": "ikebukuro"
        }
        self.park_type = ["small", "middle", "large"]
        self.medical_category_dict = {
            "hospital": "病院",
            "clinic": "診療所",
        }
        self.medical_subject_dict = {
            # "internal_medicine": "内科",
            "pediatrics": "小児科",
            # "gynecology": "婦人科",
        }
        self.school_category_dict = {
            "primary": "小学校",
            "junior_high": "中学校",
            # "high": "高等学校",
        }

    def load_data(self, remove_pref_list):
        with open(self.data_path + "station_name_dict.json", "rb") as f:
            station_name_dict = json.load(f)
        self.station_dict = {k: v for k, v in station_name_dict.items(
        ) if not v["pref"] in remove_pref_list}
        with open(self.data_path + "extracted_station_time100_transfer5.pkl", "rb") as f:
            self.extracted_stations = pickle.load(f)
        self.df_crime_rate = pd.read_csv(self.data_path + "crime_rate.csv")
        df_census = pd.read_csv(self.data_path + "census.csv")
        self.df_census = df_census[[
            "lat", "lon", "0~6age_rate", "6~18age_rate"]]
        self.df_city_park = pd.read_csv(self.data_path + "city_park.csv")
        with open("../data/hospital.pkl", "rb") as f:
            hospital_list = pickle.load(f)
        self.df_hospital = pd.DataFrame(hospital_list)
        self.df_school = pd.read_csv(self.data_path + "school.csv")
        self.df_nursery = pd.read_csv(
            self.raw_data_path + "education/nursery.csv")
        shopping_files = glob.glob(self.raw_data_path + "shopping/*.csv")
        self.df_shopping_dict = {}
        for path in shopping_files:
            cotegory = path.split('/')[-1].replace('.csv', '')
            self.df_shopping_dict[cotegory] = pd.read_csv(path)
        with open(self.raw_data_path + "restaurant/num_restaurant.json", "r") as f:
            self.restaurant_dict = json.load(f)

        self.category_dict = {
            "crime_rate": {"function": self.add_crime_rate},
            "census": {"data": self.df_census, "function": self.add_census},
            "city_park": {"data": self.df_city_park, "function": self.add_city_park},
            "medical_institution": {"data": self.df_hospital, "function": self.add_hospital},
            "school": {"data": self.df_school, "function": self.add_school},
            "education": {"data": self.df_nursery, "function": self.add_education},
            "shopping": {"data": self.df_shopping_dict, "function": self.add_shopping},
            "restaurant": {"function": self.add_restaurant},
            "transport": {"function": self.add_transport},
        }

    def remove_station(self):
        station_gcode = set()
        for i, ts in enumerate(self.terminal_station.keys()):
            df_tmp = pd.DataFrame(
                self.extracted_stations[self.station_dict[ts]["station_g_cd"]])
            if i == 0:
                station_gcode = set(df_tmp["station_g_cd"].values)
            else:
                station_gcode &= set(df_tmp["station_g_cd"].values)
        self.station_dict = {k: v for k, v in self.station_dict.items(
        ) if v['station_g_cd'] in station_gcode}

    def create_station_area_info(self):
        i = 0
        start = time.time()
        print(f"total station is {len(self.station_dict)}")
        for self.station, value in self.station_dict.items():
            self.lat = value["lat"]
            self.lon = value["lon"]
            self.station_dict[self.station]["line_num"] = len(
                self.station_dict[self.station]["line"])
            for k, v in self.category_dict.items():
                if k == "crime_rate":
                    v["function"]()
                elif k == "shopping":
                    for category, data in v["data"].items():
                        df = select_by_mesh(
                            data, self.lat, self.lon, self.dist_range)
                        v["function"](df, category)
                elif k in ["restaurant", "transport"]:
                    v["function"]()
                else:
                    df = select_by_mesh(
                        v["data"], self.lat, self.lon, self.dist_range)
                    v["function"](df)
            i += 1
            if i != 0 and i % 100 == 0:
                elapsed_time = time.time() - start
                print(f"{i}, elapsed_time:{elapsed_time}[sec]")
                start = time.time()
        self.df_station_area_info = pd.DataFrame(self.station_dict).T
        tmp = self.df_station_area_info["mun"]
        self.df_station_area_info.drop(columns="mun", inplace=True)
        self.df_station_area_info.insert(
            self.df_station_area_info.columns.get_loc("post"), "mun", tmp)

    def add_crime_rate(self):
        for p in set(self.df_crime_rate["都道府県"]):
            df_tmp = self.df_crime_rate[self.df_crime_rate["都道府県"] == p]
            value = self.station_dict[self.station]
            if value["pref"] == p:
                address = value["address"].replace("ケ", "ヶ")
                if "郡" in value["address"]:
                    address = address[address.find("郡")+1:]
                for i in df_tmp.index:
                    mun = df_tmp.loc[i, "市区町村"]
                    if address[:len(mun)] == mun:
                        self.station_dict[self.station]["mun"] = mun
                        self.station_dict[self.station]["address"] = value["address"][len(
                            mun):]
                        self.station_dict[self.station]["crime_rate"] = df_tmp.loc[i,
                                                                                   '犯罪率(件/1000人)']
                        break

    def add_census(self, df):
        df.drop(columns=["lat", "lon"], inplace=True)
        for k, v in df.mean().to_dict().items():
            self.station_dict[self.station][f"census_{k}"] = v

    def add_city_park(self, df):
        # self.station_dict[self.station][f"city_park_area"] = int(
        #     df["供用済面積（m2）"].sum())
        for pt in self.park_type:
            self.station_dict[self.station][f"city_park_{pt}"] = df[df["type"]
                                                                    == pt].shape[0]

    def add_hospital(self, df):
        for ck, cv in self.medical_category_dict.items():
            if ck == "clinic":
                df_clinic = df[df["医療機関分類"] == cv]
                self.station_dict[self.station][f"med_{ck}_all"] = df_clinic.shape[0]
                for sk, sv in self.medical_subject_dict.items():
                    tmp_num = len(
                        [subjects for subjects in df_clinic["診療科目"].values if sv in subjects])
                    self.station_dict[self.station][f"med_{ck}_{sk}"] = tmp_num
            else:
                self.station_dict[self.station][f"med_{ck}"] = df[df["医療機関分類"]
                                                                  == cv].shape[0]

    def add_school(self, df):
        for k, v in self.school_category_dict.items():
            self.station_dict[self.station][f"school_{k}"] = df[df["学校分類"]
                                                                == v].shape[0]

    def add_education(self, df):
        self.station_dict[self.station]["education_nursery"] = df.shape[0]

    def add_shopping(self, df, category):
        self.station_dict[self.station][f"shopping_{category}"] = df.shape[0]

    def add_restaurant(self):
        if type(self.dist_range) == int:
            key = str(self.dist_range)+"km"
        elif type(self.dist_range) == float:
            key = str(int(self.dist_range*1000))+"m"
        try:
            self.station_dict[self.station]["restaurant_num"] = self.restaurant_dict[self.station]["num_restaurant"][key]
        except:
            self.station_dict[self.station]["restaurant_num"] = 0

    def add_transport(self):
        time_list = []
        transfer_list = []
        for tsk, tsv in self.terminal_station.items():
            df_tmp = pd.DataFrame(
                self.extracted_stations[self.station_dict[tsk]["station_g_cd"]])
            condition = df_tmp["station_g_cd"] == self.station_dict[self.station]["station_g_cd"]
            self.station_dict[self.station][f"time_{tsv}"] = df_tmp[condition]["time_required"].values[0]
            self.station_dict[self.station][f"transfer_{tsv}"] = df_tmp[
                condition]["number_of_transfers"].values[0]
            time_list.append(df_tmp[condition]["time_required"].values[0])
            transfer_list.append(df_tmp[
                condition]["number_of_transfers"].values[0])
        self.station_dict[self.station][f"time_average"] = np.mean(
            time_list)
        self.station_dict[self.station][f"transfer_average"] = np.mean(
            transfer_list)

    def save_station_area_info(self):
        path = self.data_path + f"station_area_info_{self.dist_range}km.csv"
        self.df_station_area_info.to_csv(path)


if __name__ == "__main__":
    # Set argument
    parser = argparse.ArgumentParser()
    parser.add_argument('-dr', '--dist_range', default="1",
                        help='select dist_range within [0.5, 0.8, 1, 3, 5, 10], units:km')
    args = parser.parse_args()
    if args.dist_range in ["1", "3", "5", "10"]:
        dist_range = int(args.dist_range)
    elif args.dist_range in ["0.5", "0.8"]:
        dist_range = float(args.dist_range)
    else:
        sys.exit(
            'Failed: select dist_range within [0.5, 0.8, 1, 3, 5, 10], units:km')
    csai = CreateStationAreaInfo(dist_range)
    print("load data")
    csai.load_data(remove_pref_list=["宮城県", "福島県"])
    csai.remove_station()

    print("create station area info")
    csai.create_station_area_info()
    csai.save_station_area_info()
    print("Done")
