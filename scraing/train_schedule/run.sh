#!/usr/bin/zsh
export PYTHONPATH="$HOME/project/town-pick/town-pick/scraping/"
export PYTHONPATH="$HOME/project/town-pick/town-pick/processing/"
source ../../../bin/activate

echo "Start to create line station info"
python create_line_station_info.py

echo "Start to get station line urls in line station info"
python get_station_line_urls.py

echo "Start to get timetable urls in line station info"
python get_timetable_urls.py

echo "Start to get train schedule in line station info"
python get_train_schedule.py

echo "Start to create unfound line station info"
python create_unfound_line_station_info.py

echo "Start to get station line urls in unfound line station info"
python get_station_line_urls.py --csvfile unfound_line_station_info.csv --picklefile unfound_station_line_urls.pickle

echo "Start to get timetable urls in unfound line station info"
python get_timetable_urls.py --csvfile unfound_line_station_info.csv

echo "Start to get train schedule in unfound line station info"
python get_train_schedule.py --loadfile unfound_line_station_info.csv --picklefile train_schedule_in_unfound.pickle --savefile train_schedule_in_unfound.csv
