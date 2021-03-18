#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
import pickle
import pandas as pd
from preprocess import get_latlon


def save_latlon(path, latlon):
    with open(path, "wb") as f:
        pickle.dump(latlon, f)
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
    for path in get_latlon_list:
        path = data_path + path
        pickle_path = path.replace(".csv", ".pickle")
        df = pd.read_csv(path)

        # Check address
        if not "address" in df.columns:
            print(f"address column dosen't exist in '{path}'")
            continue
        # Check latlon
        if "lat" in df.columns:
            print(f"lat lon columns already exist in '{path}'")
            continue
        # Check pickle data
        if os.path.exists(pickle_path):
            with open(pickle_path, "rb") as f:
                latlon = pickle.load(f)
            print(f"load latlon in {pickle_path}")
        else:
            latlon = []
        skip_num = len(latlon)
        # Get latlon
        print(f"total address:{df.shape[0]}, skip_num:{skip_num} in '{path}'")
        start = time.time()
        for i, address in enumerate(df['address'].values):
            if i < skip_num:
                continue
            if " " in address:
                address = address.split(" ")[0]
            result = get_latlon(address)
            if result == "stop":
                save_latlon(pickle_path, latlon)
                sys.exit("Too Many Requests")
            else:
                latlon.append(result)
            if i != 0 and i % 10 == 0:
                save_latlon(pickle_path, latlon)
                elapsed_time = time.time() - start
                print(f"{i}, elapsed_time:{elapsed_time}[sec]")
                start = time.time()

        # Save latlon
        save_latlon(pickle_path, latlon)
        df_latlon = pd.DataFrame(latlon, columns=['lat', 'lon'])
        df = pd.concat([df, df_latlon], axis=1)
        df.to_csv(path, index=False)
        print(f"Complete {path}")
