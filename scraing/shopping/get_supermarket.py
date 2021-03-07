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
    pref_code_list = [i for i in range(11, 15)]
    df_supermarket = scraping_from_mapfan(category_id, pref_code_list)

    # Save supermarket info
    directory_path = "/home/vagrant/share/data/shopping/"
    os.makedirs(directory_path, exist_ok=True)
    df_supermarket.to_csv(directory_path + "supermarket.csv", index=False)
    print("Done!")
