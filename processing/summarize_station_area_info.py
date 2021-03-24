#!/usr/bin/env python
# coding: utf-8

import time
import json
import glob
import pickle
import pandas as pd
from preprocess import select_by_mesh


class SummarizeStationAreaInfo():
    def __init__(self, dist_range):
        self.dist_range = dist_range
        self.data_path = "../data/"
        self.raw_data_path = "/home/vagrant/share/data/"
        self.park_type = ["small", "middle", "large"]
        self.medical_category_dict = {
            "hospital": "病院",
            "clinic": "診療所",
        }
        self.medical_subject_dict = {
            "internal_medicine": "内科",
            "pediatrics": "小児科",
            "gynecology": "婦人科",
        }
        self.school_category_dict = {
            "primary": "小学校",
            "junior_high": "中学校",
            "high": "高等学校",
        }

    def load_data(self, remove_pref_list):
        with open(self.data_path + "station_name_dict.json", "rb") as f:
            station_name_dict = json.load(f)
        self.station_dict = {k: v for k, v in station_name_dict.items(
        ) if not v["pref"] in remove_pref_list}
        self.df_crime_rate = pd.read_csv(self.data_path + "crime_rate.csv")
        df_census = pd.read_csv(self.data_path + "census.csv")
        self.df_census = df_census[["lat", "lon", "single_rate",
                                    "less_than_6age_rate", "less_than_18age_rate"]]
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

        self.category_dict = {
            "census": {"data": self.df_census, "function": self.add_census},
            "city_park": {"data": self.df_city_park, "function": self.add_city_park},
            "medical_institution": {"data": self.df_hospital, "function": self.add_hospital},
            "school": {"data": self.df_school, "function": self.add_school},
            "education": {"data": self.df_nursery, "function": self.add_education},
            "shopping": {"data": self.df_shopping_dict, "function": self.add_shopping}
        }

    def create_station_area_info(self):
        i = 0
        self.add_crime_rate()
        start = time.time()
        print(f"total station is {len(self.station_dict)}")
        for self.station, value in self.station_dict.items():
            self.lat = value["lat"]
            self.lon = value["lon"]
            for k, v in self.category_dict.items():
                self.station_dict[self.station][k] = {}
                if k == "shopping":
                    for category, data in v["data"].items():
                        df = select_by_mesh(
                            data, self.lat, self.lon, self.dist_range)
                        if type(df) == pd.DataFrame:
                            v["function"](df, category)
                else:
                    df = select_by_mesh(
                        v["data"], self.lat, self.lon, self.dist_range)
                    if type(df) == pd.DataFrame:
                        v["function"](df)
            i += 1
            if i != 0 and i % 100 == 0:
                elapsed_time = time.time() - start
                print(f"{i}, elapsed_time:{elapsed_time}[sec]")
                start = time.time()

    def add_crime_rate(self):
        for p in set(self.df_crime_rate["都道府県"]):
            df_tmp = self.df_crime_rate[self.df_crime_rate["都道府県"] == p]
            for k, v in self.station_dict.items():
                if v["pref"] == p:
                    for mun in df_tmp["市区町村"]:
                        if v["address"][:len(mun)] == mun:
                            self.station_dict[k]["mun"] = mun
                            self.station_dict[k]["address"] = v["address"][len(
                                mun):]
                            break

    def add_census(self, df):
        df.drop(columns=["lat", "lon"], inplace=True)
        for k, v in df.mean().to_dict().items():
            self.station_dict[self.station]["census"][k] = v

    def add_city_park(self, df):
        for pt in self.park_type:
            self.station_dict[self.station]["city_park"][pt] = df[df["type"]
                                                                  == pt].shape[0]

    def add_hospital(self, df):
        for ck, cv in self.medical_category_dict.items():
            if ck == "clinic":
                self.station_dict[self.station]["medical_institution"][ck] = {
                }
                df_clinic = df[df["医療機関分類"] == cv]
                self.station_dict[self.station]["medical_institution"][
                    ck][ck] = df_clinic.shape[0]
                for sk, sv in self.medical_subject_dict.items():
                    tmp_num = len(
                        [subjects for subjects in df_clinic["診療科目"].values if sv in subjects])
                    self.station_dict[self.station][
                        "medical_institution"][ck][sk] = tmp_num
            else:
                self.station_dict[self.station]["medical_institution"][ck] = df[df["医療機関分類"] == cv].shape[0]

    def add_school(self, df):
        for k, v in self.school_category_dict.items():
            self.station_dict[self.station]["school"][k] = df[df["学校分類"]
                                                              == v].shape[0]

    def add_education(self, df):
        self.station_dict[self.station]["education"]["nursery"] = df.shape[0]

    def add_shopping(self, df, category):
        self.station_dict[self.station]["shopping"][category] = df.shape[0]

    def save_station_area_info(self):
        path = self.data_path + f"station_area_info_{self.dist_range}km.json"
        with open(path, "w") as f:
            json.dump(self.station_dict, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    ssai = SummarizeStationAreaInfo(dist_range=1)
    print("load data")
    remove_pref_list = ["宮城県", "福島県"]
    ssai.load_data(remove_pref_list)

    print("create station area info")
    ssai.create_station_area_info()
    ssai.save_station_area_info()
    print("Done")
