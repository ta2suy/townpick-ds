#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
import json
import requests
import xmltodict
import pandas as pd


class LatLon():
    def __init__(self):
        self.data_path = "/home/vagrant/share/data/"
        self.latlon_path = self.data_path + "etc/latlon.json"
        self.unfound_address_latlon_path = self.data_path + \
            "etc/unfound_address_latlon.json"
        self.unfound_latlon_address_path = self.data_path + \
            "etc/unfound_latlon_address.txt"
        self.get_latlon_list = [
            "shopping/shopping_mall.csv",
            "shopping/supermarket.csv",
            "shopping/baby_goods_store.csv",
            "education/nursery.csv",
            "shopping/convenience_store.csv",
        ]

    def load_data(self):
        # Load data
        address_set = set()
        for path in self.get_latlon_list:
            path = self.data_path + path
            df = pd.read_csv(path)
            # Check address
            if not "address" in df.columns:
                print(f"address column dosen't exist in '{path}'")
                continue
            address_set |= set(df["address"])

        if os.path.exists(self.unfound_latlon_address_path):
            with open(self.unfound_latlon_address_path, "r") as f:
                content = f.readlines()
            unfound_latlon_address = set(x.strip() for x in content)
        else:
            unfound_latlon_address = set()

        # Check json data
        if os.path.exists(self.latlon_path):
            with open(self.latlon_path, "r") as f:
                self.latlon = json.load(f)
            print(f"load latlon")
        else:
            self.latlon = {}

        address_set = address_set - set(self.latlon.keys())
        address_set = address_set - unfound_latlon_address
        return address_set

    def get_latlon(self, address: str):
        url = "http://www.geocoding.jp/api/"
        payload = {"q": address}
        result = requests.get(url, params=payload)
        time.sleep(10)
        resultdict = xmltodict.parse(result.text)
        try:
            if resultdict["html"]["head"]["title"] == "Too Many Requests":
                return "stop"
        except:
            try:
                lat = resultdict["result"]["coordinate"]["lat"]
                lon = resultdict["result"]["coordinate"]["lng"]
                return lat, lon
            except:
                with open(self.unfound_latlon_address_path, "a") as f:
                    print(address, file=f)
                print(f"Not found latlon in '{address}'")
                return None, None

    def save_latlon(self):
        with open(self.latlon_path, "w") as f:
            json.dump(self.latlon, f, indent=4, ensure_ascii=False)
            print("Save latlon up to now")

    def add_latlon_to_csv(self):
        df_latlon = pd.DataFrame(self.latlon).T
        df_latlon.reset_index(inplace=True)
        df_latlon.columns = ["address", "lat", "lon"]
        for path in self.get_latlon_list:
            path = self.data_path + path
            df = pd.read_csv(path)
            df = pd.merge(df, df_latlon, on="address", how="left")
            df.to_csv(path, index=False)

    def get_latlon_for_unfound(self):
        df_latlon = pd.DataFrame(self.latlon).T
        df_latlon.columns = ["lat", "lon"]
        df_unfound = df_latlon[df_latlon["lat"].isnull()]
        print(f"total unfound address is {df_unfound.shape[0]}")
        for address in df_unfound.index:
            result = self.get_latlon(address)
            if result == "stop":
                self.save_latlon()
                sys.exit("Too Many Requests")
            else:
                print(address, result)
                self.latlon[address] = result

    def complement_latlon(self):
        if os.path.exists(self.unfound_address_latlon_path):
            with open(self.unfound_address_latlon_path, "r") as f:
                unfound_address_latlon = json.load(f)
            for k, v in unfound_address_latlon.items():
                self.latlon[k] = v

    def main(self, address):
        if " " in address:
            address = address.split(" ")[0]
        result = self.get_latlon(address)
        if result == "stop":
            self.save_latlon()
            sys.exit("Too Many Requests")
        else:
            self.latlon[address] = result


if __name__ == '__main__':
    # Load data
    ll = LatLon()
    address_set = ll.load_data()

    # Get latlon
    print("get latlon")
    print(f"total address:{len(address_set)}")
    start = time.time()
    for i, address in enumerate(address_set):
        ll.main(address)
        if i != 0 and i % 10 == 0:
            ll.save_latlon()
            elapsed_time = time.time() - start
            print(f"{i}, elapsed_time:{elapsed_time}[sec]")
            start = time.time()
    ll.get_latlon_for_unfound()
    ll.complement_latlon()

    # Save latlon
    ll.save_latlon()
    ll.add_latlon_to_csv()
    print(f"Done!")
