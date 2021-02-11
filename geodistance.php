<?php

ini_set('memory_limit', '-1');
ini_set("display_errors", true);
ini_set("error_reporting", E_ALL);

use Ayeo\Geo\Coordinate;
use Ayeo\Geo\DistanceCalculator;

require __DIR__ . "/vendor/autoload.php";

try {
    // delimiters
    $inDelimiter = $argv[1] ?? '';
    if ($inDelimiter == '-t') { $inDelimiter = "\t"; }
    if ($inDelimiter == '') { throw new \Exception("Input delimiter cannot be empty!"); }
    $outDelimiter = $argv[2] ?? '';
    if ($outDelimiter == '-t') { $outDelimiter = "\t"; }
    if ($outDelimiter == '') { $outDelimiter = $inDelimiter; }

    // LAT field
    $inLatField = intval($argv[3] ?? '') - 1;
    // LNG field
    $inLngField = intval($argv[4] ?? '') - 1;
    if ($inLatField == $inLngField || $inLatField < 0 || $inLngField < 0) {
        throw new Exception("Input LAT and LNG fields incorrect! They cannot be equal and greater than 0!");
    }

    // identifier field
    $identifierField = intval($argv[5] ?? '') - 1;
    if ($identifierField < 0) {
        throw new Exception("Identifier field incorrect! It must be greater than 0!");
    }

    // min distance between points
    $minDistance = intval($argv[6] ?? '');

    // init input stream
    $fin = fopen('php://stdin', 'r');
    // init output stream
    $stdout = fopen('php://stdout', 'w');

    // extract only lines for identifier having coordinates further apart than min distance
    $calculator = new DistanceCalculator();
    $previousData = [];
    $coordinatesArr = [];

    while(!feof($fin)) {
        $line = str_replace(array("\n", "\r", "\""), '', fgets($fin));
        if ($line != '') {
            if (strpos($line, $inDelimiter) === false) { continue; }
            
            // get data from line
            $data = explode($inDelimiter, $line);

            if (sizeof($previousData) == 0 || $previousData[$identifierField] != $data[$identifierField]) { // first or new identifier
                fwrite($stdout, implode($outDelimiter, $data) . PHP_EOL);

                // init coordinates array with current coordinates
                $coordinatesArr = [new Coordinate\Decimal(floatval($data[$inLatField]), floatval($data[$inLngField]))];
            } else { // same identifier
                // init current coordinates
                $currentCoordinates = new Coordinate\Decimal(floatval($data[$inLatField]), floatval($data[$inLngField]));

                // check if current coordinates are further than the minimum distance to all other coordinates of the same identifier
                $farEnough = true;
                foreach ($coordinatesArr as $coordinates) {
                    if ($calculator->getDistance($coordinates, $currentCoordinates) < $minDistance) {
                        $farEnough = false;
                        break;
                    }
                }
                if ($farEnough) {
                    fwrite($stdout, implode($outDelimiter, $data) . PHP_EOL);
                }

                // add current coordinates to array
                $coordinatesArr[] = $currentCoordinates;
            }

            $previousData = $data;
        }
    }

    exit(0);

} catch (\Exception $e) {
    echo $e->getMessage() . "\n";
    exit(1);
}
