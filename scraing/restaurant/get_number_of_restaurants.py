#!/usr/bin/env python
# coding: utf-8

import time
from restaurant import GetNumRestaurant


if __name__ == '__main__':
    gnr = GetNumRestaurant()
    # Load data
    num_restaurant_dict, station_list, unfound_station_dict = gnr.load_dataset()

    # Get number of restaurants around the station
    print(f"total station length: {len(station_list)}")
    for i, s in enumerate(station_list):
        print(i+1, s)
        start = time.time()
        if "(" in s:
            num = s.find("(")
            station = s[:num] + "駅"
            check_station = station + s[num:]
        else:
            station = s + "駅"
            check_station = s + "駅"
        if check_station in unfound_station_dict.keys():
            print("skip")
            continue
        restaurant_dict = gnr.get_number_of_restaurants(
            station, check_station, unfound_station_dict)
        if restaurant_dict:
            num_restaurant_dict[s]['num_restaurant'] = restaurant_dict
        else:
            print(f"Don't find {check_station}")

        elapsed_time = time.time() - start
        print(f"elapsed_time:{elapsed_time}[sec]")
        if i != 0 and i % 5 == 0:
            gnr.save_dict(num_restaurant_dict, unfound_station_dict)
            print("Save dicts until now")

    # Save station_num_restaurant_dict
    gnr.save_dict(num_restaurant_dict, unfound_station_dict)
    print("Done!")
