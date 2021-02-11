<?php

ini_set('memory_limit', '-1');
ini_set("display_errors", true);
ini_set("error_reporting", E_ALL);

use Location\Coordinate;
use Location\Polygon;

require __DIR__ . "/vendor/autoload.php";

const NUMBER_ARGS_BEFORE_POLYGONS = 4;

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

    // polygon files
    $firstPolygonFileArg = NUMBER_ARGS_BEFORE_POLYGONS + 1;
    $totalPolygonFileArgs = $argc;
    for ($p = $firstPolygonFileArg; $p < $totalPolygonFileArgs; $p++) {
        $polygonFile = $argv[$p] ?? '';
        if (!file_exists($polygonFile)) {
            throw new \Exception("Polygon file <$polygonFile> does not exist!");
        }

        // init polygon data
        $polygon = json_decode(file_get_contents($polygonFile));
        if ($polygon->lat_index == $polygon->lng_index || !in_array($polygon->lat_index, [0,1]) || !in_array($polygon->lng_index, [0,1])) {
            throw new \Exception("Polygon lat and lng must be either 1 or 0 and cannot be of the same value!");
        }
        if ($totalCoordinates = sizeof($polygon->coordinates) < 3) {
            throw new \Exception("Polygon must have at least 3 pairs of lat/lng coordinates, only $totalCoordinates given!");
        }

        // load polygon coordinates
        $geofences[] = new Polygon();
        foreach ($polygon->coordinates as $polygonCoordinates) {
            $geofences[sizeof($geofences)-1]->addPoint(new Coordinate($polygonCoordinates[$polygon->lat_index], $polygonCoordinates[$polygon->lng_index]));
        }
    }

    // init input stream
    $fin = fopen('php://stdin', 'r');
    // init output stream
    $stdout = fopen('php://stdout', 'w');

    // extract only lines with coordinates within polygon
    while(!feof($fin)) {
        $line = str_replace(array("\n", "\r", "\""), '', fgets($fin));
        if ($line != '') {
            if (strpos($line, $inDelimiter) === false) { continue; }
            $data = explode($inDelimiter, $line);

            try {
                $c = new Coordinate(floatval($data[$inLatField]), floatval($data[$inLngField]));
                foreach ($geofences as $geofence) {
                    if ($geofence->contains($c)) {
                        fwrite($stdout, implode($outDelimiter, $data) . PHP_EOL);
                        break;
                    }
                }
            } catch (\Exception $e) {
                // ignore non geofence-able lines
            }
        }
    }

    exit(0);

} catch (\Exception $e) {
    echo $e->getMessage() . "\n";
    exit(1);
}
