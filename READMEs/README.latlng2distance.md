# LAT/LNG source + destination to distance (km/miles)

## Introduction

Look up lat/lng pairs from a given input file and append distance in km or miles to the input data onto an output file:

input | output
----- | ------
40.6976637 -74.1197643 39.7645187 -104.9951948 | -74.1197643 -74.1197643 39.7645187 -104.9951948 **2609.59**

## Installation

Install `python3`, `pip3` and necessary `libraries`
```
sudo apt install python3-pip
pip3 install numpy
```

## Usage
```
python3 latlng2distance.py -h/--help
```

**`TIPS:`**
Make sure to **sort** the input file on the **lat** and **lng** fields to reduce the processing time greatly.

## Notes

**The input must be `2 lines` long or more as they are required to determine the presence of headers**

Useful links to documentation and tools:
- This tool is based on [Haversine formula](https://en.wikipedia.org/wiki/Haversine_formula)
- Explanations by [Towards Data Science](https://towardsdatascience.com/heres-how-to-calculate-distance-between-2-geolocations-in-python-93ecab5bbba4)

