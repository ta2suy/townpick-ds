#!/bin/bash

source ../../../bin/activate

echo "Start to create line station info"
python create_line_station_info.py

echo "Start to get station line urls"
python get_station_line_urls.py

echo "Start to get timetable urls"
python get_timetable_urls.py

echo "Start to get train schedule"
python get_train_schedule.py
