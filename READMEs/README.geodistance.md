# Filter data farther than a given minimum distance

## Introduction
This library filter location data located farther than a given minimum **distance²** from all parsed locations for a same **identifier¹** and outputs whole matching lines (every fields).

It uses STDIN and STDOUT in order to boost the process avoiding disk I/O. This allows piping this process in a more elaborate script.

## Important notes
`Make sure that none of the delimiters are contained inside a double quoted string.`  
`e.g.: "this,is,a,string" in a CSV file`  
A great tool to deal with this case and prepare your data is [csvquote](https://github.com/dbro/csvquote).

This process will remove double quotes anyway but will not deal with inside-string-delimiter.

Lines with no separator matching `INPUT_DELIMITER` will be skipped, no error will be displayed.

`The data MUST BE SORTED ON THE IDENTIFIER¹ or the output will not be filtered as expected!`

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
 $5  = IDENTIFIER_FIELD:                  Identifier¹ field #
 $6  = DISTANCE:                          Distance in meters²
```
¹ `Identifier` is the data that links different lines together and on which you wish to filter the dataset   
² `Distance` must be given in METERS    

## Examples
read in `CSV`, output same type, filter out all locations closer than 10km from each others for a same id
```
cat examples/geodistance/data.csv | php geodistance.php , , 2 3 1 10000
```
