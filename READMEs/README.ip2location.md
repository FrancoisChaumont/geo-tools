# IP to country & state offline lookup tool

## Introduction

Look up IP addresses from a given input file and append country & state (in ISO2 format) to the input data onto a given output file:

input | output
----- | ------
99.99.8.233 | 99.99.8.233 **US** **IL**

## Installation

Run the following command to build the library:
```
composer install
```

Then follow these steps:

1. Delete the folders `geoip2`, `maxmind` and `maxmind-db` inside [vendor](../vendor)
2. Extract the content of [ip2location.vendors.tar.gz](../extra/ip2location.vendors.tar.gz) into [vendor](../vendor)
3. Download the latest [GeoLite2 City database](https://dev.maxmind.com/geoip/geoip2/geolite2) (file `GeoLite2-City.mmdb`) into [databases](../databases)

## Usage

Run `php ip2location.php --help` for usage details.

**`WARNING:`**
Keep in mind that the entire **input** file is **buffered** as well for improved performance.

**`TIPS:`**
Make sure to **sort** the input file on the **IP field** to reduce the processing time greatly.

## Notes

This tool is based on [MaxMind GeoIP2](https://packagist.org/packages/geoip2/geoip2) project.

However, a forked version of MaxMind GeoIP2 is used to allow buffering of the entire database for improved performance.

Modifications applied to:
- `MaxMind Reader class constructor` > vendor\geoip2\geoip2\src\Database\Reader.php
- `GeoIP2 Reader class constructor` > vendor\maxmind-db\reader\src\MaxMind\Db\Reader.php

