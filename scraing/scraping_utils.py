#!/usr/bin/env python
# coding: utf-8

import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_soup(url: str, sleep_sec=3):
    response = requests.get(url)
    time.sleep(sleep_sec)
    return BeautifulSoup(response.text, 'html.parser')


def set_driver():
    # Set driver
    opt = Options()
    opt.add_argument('--headless')
    # Open browser
    driver = webdriver.Chrome(options=opt)
    return driver
