# LAT/LNG to country offline look up tool

## Introduction

Look up lat/lng from a given input file and append country (in ISO2 format) to the input data onto a output file:

input | output
----- | ------
-37.775842 144.97164 | -37.775842 144.97164 **AU**

## Installation

Install `python3`, `pip3` and necessary `libraries`
```
sudo apt install python3-pip
sudo pip3 install reverse_geocoder
sudo pip3 install smart_open

```
Makes sure the library `requests` is up-to-date
```
sudo pip3 install --upgrade requests
```

## Customization

Customize the input file headers, the field extractions from a line and the outline to adapt to your input and output requirement.  
Look for `""" CUSTOMIZE HERE """` in [latlng2location.py](../latlng2location.py) file.

## Usage
```
cat input_file | python3 latlng2location.py > output_file
```

**`TIPS:`**
Make sure to **sort** the input file on the **lat** and **lng** fields to reduce the processing time greatly.

## Notes

This tool is based on [thampiman/reverse-geocoder](https://github.com/thampiman/reverse-geocoder)

## Todo

- Investigate multithreading by sending all coordinates at once for improved performance (see repository for more details).
- Pass the delimiter as argument to the script
- Pass input file headers to the script
- Adjust outline to headers argument
