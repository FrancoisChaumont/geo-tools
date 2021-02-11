# Geofence data within one or multiple polygons

## Introduction
This library geofence location data located within given polygon(s) and outputs whole matching lines (every fields).

It uses STDIN and STDOUT in order to boost the process avoiding disk I/O. This allows piping this process in a more elaborate script.

## Important notes
`Make sure that none of the delimiters are contained inside a double quoted string.`  
`e.g.: "this,is,a,string" in a CSV file`  
A great tool to deal with this case and prepare your data is [csvquote](https://github.com/dbro/csvquote).

This process will remove double quotes anyway but will not deal with inside-string-delimiter.

Lines with no separator matching `INPUT_DELIMITER` will be skipped, no error will be displayed.

## Requirements
[Composer](https://getcomposer.org/download) must be installed in order to use this library.

## Installation
Run the following command to build the library:
```
composer install
```

## Usage
```
php geofence.php $1 $2 $3 $4 $5+

 $1  = INPUT_DELIMITER:                   Input (STDIN) field delimiter
 $2  = OUTPUT_DELIMITER:                  Output field delimiter >>> defaults to same as input
 $3  = INPUT_LAT_FIELD:                   Input latitude field #
 $4  = INPUT_LNG_FIELD:                   Input longitude field #
 $5+ = POLYGON_FILES:                     Polygon files containing their coordinates
```

## Notes

`lat_index` and `lng_index` in the polygon.json files is used to indicate which, from the coordinate pairs, is latitude and which is longitude.  
For example, [polygon.json](../examples/geofence/polygon.json) has lng/lat pairs and [polygon2.json](../examples/geofence/polygon2.json) has lat/lng pairs.

## Examples
read in `CSV`, output same type
```
cat examples/geofence/data.csv | php geofence.php , '' 1 2 examples/geofence/polygon.json
```

read in `CSV`, output same type (multi-polygon)
```
cat examples/geofence/data.csv | php geofence.php , '' 1 2 examples/geofence/polygon.json examples/geofence/polygon2.json
```

read in `CSV`, output `CSV`
```
cat examples/geofence/data.csv | php geofence.php , , 1 2 examples/geofence/polygon.json
```

read in `CSV`, output `PSV`
```
cat examples/geofence/data.csv | php geofence.php , '|' 1 2 examples/geofence/polygon.json
```

read in `CSV`, output `TSV`
```
cat examples/geofence/data.csv | php geofence.php , -t 1 2 examples/geofence/polygon.json
```

read in `PSV`, output `PSV`
```
cat examples/geofence/data.psv | php geofence.php '|' '' 1 2 examples/geofence/polygon.json
```

read in `PSV`, output `CSV`
```
cat examples/geofence/data.psv | php geofence.php '|' ',' 1 2 examples/geofence/polygon.json
```

read in `PSV`, output `TSV`
```
cat examples/geofence/data.psv | php geofence.php '|' -t 1 2 examples/geofence/polygon.json
```

read in `TSV` passing tabulation directly (`"$(echo -en '\t')"`)
```
cat examples/geofence/data.tsv | php geofence.php "$(echo -en '\t')" "$(echo -en '\t')" 1 2 examples/geofence/polygon.json
```

read in `TSV` passing the parameter `-t` for tabulation
```
cat examples/geofence/data.tsv | php geofence.php -t -t 1 2 examples/geofence/polygon.json
```

read in `TSV`, output `CSV`
```
cat examples/geofence/data.tsv | php geofence.php -t , 1 2 examples/geofence/polygon.json
```

read in `TSV`, output `PSV`
```
cat examples/geofence/data.tsv | php geofence.php -t '|' 1 2 examples/geofence/polygon.json
```

count total of location falling inside the polygon
```
cat examples/geofence/data.csv | php geofence.php , , 1 2 examples/geofence/polygon.json | wc -l
```

sort + dedupe locations falling inside the polygon
```
cat examples/geofence/data.csv | php geofence.php , , 1 2 examples/geofence/polygon.json | sort -t, -k1,1n -k2,2n -u
```

sort + count duplicate locations falling inside the polygon
```
cat examples/geofence/data.csv | php geofence.php , , 1 2 examples/geofence/polygon.json | sort -t, -k1,1n -k2,2n | uniq -c
```

read in `CSV` double quoted, output `CSV`
```
cat examples/geofence/data-quoted.csv | php geofence.php , , 1 2 examples/geofence/polygon.json
```

read in `CSV` double quoted with inside-string-delimiter, output `CSV`
```
csvquote examples/geofence/data-quoted.inside-delimiter.csv | sed 's/\x1F//g' | php geofence.php , , 1 2 examples/geofence/polygon.json
```

read in `TSV` double quoted with inside-string-delimiter, output `CSV`
```
csvquote -t examples/geofence/data-quoted.inside-delimiter.tsv | sed 's/\x1F//g' | php geofence.php -t , 1 2 examples/geofence/polygon.json
```

read in `TSV` double quoted with inside-string-delimiter, output `TSV`
```
csvquote -t examples/geofence/data-quoted.inside-delimiter.tsv | sed 's/\x1F//g' | php geofence.php -t -t 1 2 examples/geofence/polygon.json
```

read in `CSV` passing tabulation as INPUT_DELIMITER, no output - no error
```
cat examples/geofence/data.csv | php geofence.php -t , 1 2 examples/geofence/polygon.json
```

