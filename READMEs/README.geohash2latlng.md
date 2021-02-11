# Geohash to LAT/LNG

## Introduction

Look up geohash from a given input file and append lat/lng to the input data onto a output file:

input | output
----- | ------
ezs42 | ezs42 **42.6 -5.6**

## Installation

Install `python3`, `pip3` and necessary `libraries`
```
sudo apt install python3-pip
pip3 install python-geohash
```
*Latest version of python-geohash may require python3.8 to run the script*

## Usage
```
python3 geohash2latlng.py -h/--help
```

**`TIPS:`**
Make sure to **sort** the input file on the **geohash** fields to reduce the processing time greatly.

## Notes

**The input must be `2 lines` long or more as they are required to determine the presence of headers**

Useful links to documentation and tools:
- This tool is based on [python-geohash](https://pypi.org/project/python-geohash)
- More info about geohashing [Wikipedia](https://en.wikipedia.org/wiki/Geohash)
