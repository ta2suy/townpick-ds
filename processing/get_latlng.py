#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
import glob
import pickle
import pandas as pd
from preprocess import get_latlng


def save_latlng(path, latlng):
    with open(path, "wb") as f:
        pickle.dump(latlng, f)
        print("Save latlng up to now")


if __name__ == '__main__':
    data_path = "/home/vagrant/share/data/shopping/*.csv"
    csv_files = glob.glob(data_path)
    csv_files.sort()
    print(f"All csv files are {csv_files}")
    for path in csv_files:
        if "convenience_store" in path:
            continue
        pickle_path = path.replace(".csv", ".pickle")
        df = pd.read_csv(path)
        if not "address" in df.columns:
            print(f"address column dosen't exist in '{path}'")
            continue
        if "lat" in df.columns:
            print(f"lat lng columns already exist in '{path}'")
            continue

        if os.path.exists(pickle_path):
            with open(pickle_path, "rb") as f:
                latlng = pickle.load(f)
            print(f"load latlng in {pickle_path}")
        else:
            latlng = []
        skip_num = len(latlng)
        print(f"total address:{df.shape[0]}, skip_num:{skip_num} in '{path}'")
        start = time.time()
        for i, address in enumerate(df['address'].values):
            if i < skip_num:
                continue
            result = get_latlng(address)
            if result == "stop":
                save_latlng(pickle_path, latlng)
                sys.exit("Too Many Requests")
            else:
                latlng.append(result)
            if i != 0 and i % 10 == 0:
                save_latlng(pickle_path, latlng)
                elapsed_time = time.time() - start
                print(f"{i}, elapsed_time:{elapsed_time}[sec]")
                start = time.time()

        save_latlng(pickle_path, latlng)
        df_latlon = pd.DataFrame(latlng, columns=['lat', 'lng'])
        df = pd.concat([df, df_latlon], axis=1)
        df.to_csv(path, index=False)
        print("Complete {path}")
