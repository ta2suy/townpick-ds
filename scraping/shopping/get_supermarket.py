#!/usr/bin/env python
# coding: utf-8

import os
import sys
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraping_utils import scraping_from_navitime, scraping_from_mapfan  # nopep8


if __name__ == '__main__':
    # # Get supermarket info from navitime
    # category_id = "0202"
    # pref_code_list = [i for i in range(11, 15)]
    # df_supermarket = scraping_from_navitime(category_id, pref_code_list)

    # Get supermarket info from mapfan
    category_id = "16"
    pref_code_list = [8, 9, 10, 19, 20, 22]
    df_supermarket = scraping_from_mapfan(category_id, pref_code_list)

    # Save supermarket info
    directory_path = "/home/vagrant/share/data/shopping/"
    os.makedirs(directory_path, exist_ok=True)
    save_path = directory_path + "supermarket.csv"
    if os.path.exists(save_path):
        df = pd.read_csv(save_path)
        df_supermarket = pd.concat([df, df_supermarket])
    df_supermarket.to_csv(save_path, index=False)
    print("Done!")
