#!/usr/bin/env python
# coding: utf-8

import os
import sys
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraping_utils import scraping_from_mapfan  # nopep8


if __name__ == '__main__':
    # Get baby goods store info
    category_id = "1021"
    pref_code_list = [8, 9, 10, 11, 12, 13, 14, 19, 20, 22]
    df_baby_goods_store = scraping_from_mapfan(category_id, pref_code_list)

    # Save baby goods store info
    directory_path = "/home/vagrant/share/data/shopping/"
    os.makedirs(directory_path, exist_ok=True)
    save_path = directory_path + "baby_goods_store.csv"
    if os.path.exists(save_path):
        df = pd.read_csv(save_path)
        df_baby_goods_store = pd.concat([df, df_baby_goods_store])
    df_baby_goods_store.to_csv(save_path, index=False)
    print("Done!")
