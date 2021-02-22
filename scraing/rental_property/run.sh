#!/usr/bin/zsh
export PYTHONPATH="$HOME/project/town-pick/town-pick/scraping/"
source ../../../bin/activate

echo "Start to get rental property"
python get_rental_property.py
