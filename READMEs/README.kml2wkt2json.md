# KML to WKT/JSON

## Introduction

Turn a KML file into a WKT/JSON file for Athena geofence with the following format:
```
{"boundaryshape":"POLYGON ((LNG LAT, ...))","name":"POLYGON_NAME","locality":"LOCALITY"}
```

## Requirements

- PHP7.3+

## Installation

None

## Usage

```
php kml2wkt2json.php POLYGONS_FILE.kml LOCALITY
```

The output file is saved under `input_file_name.kml.wkt.json`.

