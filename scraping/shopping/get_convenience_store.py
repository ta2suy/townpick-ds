#!/usr/bin/env python
# coding: utf-8

import os
import sys
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraping_utils import scraping_from_navitime  # nopep8


if __name__ == '__main__':
    # Get convenience store info
    category_id = "0201"
    pref_code_list = [8, 9, 10, 11, 12, 13, 14, 19, 20, 22]
    df_convenience_store = scraping_from_navitime(category_id, pref_code_list)
    df_convenience_store.drop_duplicates("name", inplace=True)
    df_convenience_store.reset_index(drop=True, inplace=True)

    # Save convenience store info
    directory_path = "/home/vagrant/share/data/shopping/"
    os.makedirs(directory_path, exist_ok=True)
    save_path = directory_path + "convenience_store.csv"
    if os.path.exists(save_path):
        df = pd.read_csv(save_path)
        df_convenience_store = pd.concat([df, df_convenience_store])
    df_convenience_store.to_csv(save_path, index=False)
    print("Done!")
