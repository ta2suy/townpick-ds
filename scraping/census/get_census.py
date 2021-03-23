#!/usr/bin/env python
# coding: utf-8

import re
import os
import sys
import time
import glob
import shutil
import pickle
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scraping_utils import get_soup, set_driver  # nopep8


e_stat_url = 'https://www.e-stat.go.jp/'
rec = re.compile('\d+')
driver = set_driver()
css_selector = 'body > div.dialog-off-canvas-main-canvas > div > main > div.row.l-estatRow > section > div.region.region-content > div > div > div.stat-content.fix > section > section > div > div.stat-search_result-files > div > div:nth-child(2) > a'


def get_pref_urls(url, css_selector):
    driver.get(url)
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "stat-title")))
    driver.find_element_by_css_selector(css_selector).click()
    time.sleep(10)

    css_selector = 'body > div.dialog-off-canvas-main-canvas > div > main > div.row.l-estatRow > section > div.region.region-content > div > div > div.stat-content.fix > section > section > div > div.stat-search_main > div.stat-search_result-list.js-items.stat-auxiliary_line > ul:nth-child(14) > li > div.js-toggle'
    response = driver.find_element_by_css_selector(css_selector)
    soup = BeautifulSoup(response.get_attribute('innerHTML'), 'html.parser')
    urls = []
    for s in soup('a'):
        urls.append(e_stat_url + s.get('href'))

    return urls[:-1]


def get_urls(soup, use_index):
    tmp = soup(
        class_='stat-dataset_list-body')[0](class_='stat-dataset_list-detail')
    urls = []
    for t in tmp:
        try:
            idx = int(rec.findall(
                t(class_='stat-dataset_list-border-top')[0].text)[0])
            if idx in use_index:
                urls.append(e_stat_url+t('a')[0].get('href'))
        except:
            pass
    return urls


def download_csv(url):
    driver.get(url)
    WebDriverWait(driver, 30).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "stat-resource_download_filed_title")))
    driver.find_element_by_css_selector(css_selector).click()


def move_files(dir_path, num_files):
    while True:
        time.sleep(10)
        if len(glob.glob('./*.csv')) == num_files:
            for p in glob.glob('./*.csv'):
                shutil.move(p, dir_path)
            break


if __name__ == '__main__':
    year = 2015  # select 2015
    census_path = f'/home/vagrant/share/data/census/{year}/'
    census_urls_path = census_path + 'urls.pkl'
    if os.path.exists(census_urls_path):
        print('load census urls')
        with open(census_urls_path, 'rb') as f:
            pref_urls = pickle.load(f)

    else:
        print('get census urls')
        if year == 2015:
            url_2015 = e_stat_url + 'stat-search/files?page=1&toukei=00200521&tstat=000001080615'
            css = 'body > div.dialog-off-canvas-main-canvas > div > main > div.row.l-estatRow > section > div.region.region-content > div > div > div.stat-content.fix > section > section > div > div.stat-search_main > div.stat-search_result-list.js-items.stat-auxiliary_line > ul:nth-child(14) > li > div.stat-search_result-item2-sub.fix.js-item2_parent.stat-item2_parent.js-item_child.js-has-child.stat-has-child.stat-odd_items > span.stat-title-has-child > span.js-click.stat-icon'
            pref_urls = get_pref_urls(url_2015, css)

        with open(census_urls_path, 'wb') as f:
            pickle.dump(pref_urls, f)

    print('get census data')
    pref_path = '/home/vagrant/share/data/etc/pref.csv'
    df_pref = pd.read_csv(pref_path)
    df_pref.set_index('id', inplace=True)
    use_index = [3, 6, 7, 8]

    for i, pref_url in enumerate(pref_urls):
        start = time.time()
        soup = get_soup(pref_url)
        pref_id = soup(
            class_='stat-dataset_sheet')[0]('tr')[-1]('td')[0].text[:2]
        dir_name = pref_id + '_' + \
            df_pref.loc[int(pref_id)]['romaji'] + '/'
        dir_path = census_path + dir_name
        if os.path.exists(dir_path):
            print(f"{dir_path} already exist")
            continue
        else:
            os.makedirs(dir_path, exist_ok=True)
            urls = get_urls(soup, use_index)
            for url in urls:
                download_csv(url)

            move_files(dir_path, len(use_index))

        elasped_time = time.time() - start
        print(dir_name, elasped_time)
    print('Done!')
