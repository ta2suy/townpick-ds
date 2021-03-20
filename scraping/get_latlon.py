#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
import json
import requests
import xmltodict
import pandas as pd


def get_latlon(address: str):
    url = 'http://www.geocoding.jp/api/'
    payload = {'q': address}
    result = requests.get(url, params=payload)
    time.sleep(10)
    resultdict = xmltodict.parse(result.text)
    try:
        if resultdict['html']['head']['title'] == "Too Many Requests":
            return "stop"
    except:
        try:
            lat = resultdict["result"]["coordinate"]["lat"]
            lon = resultdict["result"]["coordinate"]["lon"]
            return lat, lon
        except:
            print(f"Not found latlon in '{address}'")
            return None, None


def save_latlon(path: str, latlon: dict):
    with open(path, "w") as f:
        json.dump(latlon, f, indent=4, ensure_ascii=False)
        print("Save latlon up to now")


if __name__ == '__main__':
    # Load data
    data_path = "/home/vagrant/share/data/"
    get_latlon_list = [
        'shopping/shopping_mall.csv',
        'shopping/supermarket.csv',
        'shopping/baby_goods_store.csv',
        'education/nursery.csv',
        'shopping/convenience_store.csv',
    ]
    address_set = set()
    for path in get_latlon_list:
        path = data_path + path
        df = pd.read_csv(path)
        # Check address
        if not "address" in df.columns:
            print(f"address column dosen't exist in '{path}'")
            continue
        address_set |= set(df['address'])

    # Check json data
    latlon_path = data_path + "etc/latlon.json"
    if os.path.exists(latlon_path):
        with open(latlon_path, "r") as f:
            latlon = json.load(f)
        print(f"load latlon in {latlon_path}")
    else:
        latlon = {}
    # Get latlon
    address_set = address_set - set(latlon.keys())
    print(f"total address:{len(address_set)}")
    start = time.time()
    for i, address in enumerate(address_set):
        if " " in address:
            address = address.split(" ")[0]
        result = get_latlon(address)
        if result == "stop":
            save_latlon(latlon_path, latlon)
            sys.exit("Too Many Requests")
        else:
            latlon[address] = result
        if i != 0 and i % 10 == 0:
            save_latlon(latlon_path, latlon)
            elapsed_time = time.time() - start
            print(f"{i}, elapsed_time:{elapsed_time}[sec]")
            start = time.time()

    # Save latlon
    save_latlon(latlon_path, latlon)
    df_latlon = pd.DataFrame(latlon).T
    df_latlon.reset_index(inplace=True)
    df_latlon.columns = ['address', 'lat', 'lon']
    for path in get_latlon_list:
        path = data_path + path
        df = pd.read_csv(path)
        df = pd.merge(df, df_latlon, on='address')
        df.to_csv(path, index=False)
    print(f"Done!")
