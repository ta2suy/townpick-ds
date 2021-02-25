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
    pref_code_list = [i for i in range(11, 15)]
    df_convenience_store = scraping_from_navitime(category_id, pref_code_list)

    # Save convenience store info
    save_path = "/home/vagrant/share/data/shopping/convenience_store.csv"
    df_convenience_store.to_csv(save_path, index=False)
    print("Done!")
