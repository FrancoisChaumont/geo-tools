<?php

/**
 * Take a KML formatted polygon file as input and output a WKT/JSON file of the following format:
 * {"boundaryshape":"POLYGON ((LNG LAT, ...))","name":"POLYGON_NAME","locality":"LOCALITY"}
 * 
 * The output file is saved under input_file_name.kml.wkt.json
 * 
 * USAGE:
 * arg #1: polygon file path
 * arg #2: locality name to appear in the output locality node
 * 
 * php kml2wkt2json.php POLYGONS_FILE.kml LOCALITY
 */

ini_set('memory_limit', '-1');
ini_set("display_errors", true);
ini_set("error_reporting", E_ALL);

// input configuration
const IN_DOCUMENT_NODE = 'Document';
const IN_PLACEMARK_NODE = 'Placemark';
const IN_NAME_NODE = 'name';
const IN_POLYGON_NODE = 'Polygon';
const IN_MULTIGEOMETRY_NODE = 'MultiGeometry';
const IN_OUTERBOUNDARYIS_NODE = 'outerBoundaryIs';
const IN_LINEARRING_NODE = 'LinearRing';
const IN_COORDINATES_NODE = 'coordinates';

// output configuration
const OUT_WKT_NODE = 'boundaryshape';
const OUT_NAME_NODE = 'name';
const OUT_LOCALITY_NODE = 'locality';
const OUT_MULTIPOLYGON_HEADER = 'MULTIPOLYGON';
const OUT_POLYGON_HEADER = 'POLYGON';

try {
    if (!isset($argv[1])) { throw new \Exception("Missing input KML file! [arg #1]"); }
    if (!isset($argv[2])) { throw new \Exception("Missing locality! [arg #2]"); }

    $xmlfile = $argv[1];
    $locality = strtolower($argv[2]);

    // verify if the file exists
    if (!is_readable($xmlfile)) { throw new \Exception("Input file does not exist!"); }
    
    // attemp to read load the file
    if (($xml = simplexml_load_file($xmlfile)) === false) { throw new \Exception("Loading XML file failed!"); }
    
    // verify the expected format of the file
    if (!property_exists($xml, IN_DOCUMENT_NODE)) { throw new \Exception(printf("Node <%s> not found!", IN_DOCUMENT_NODE)); }
    if (!property_exists($xml->{IN_DOCUMENT_NODE}, IN_PLACEMARK_NODE)) { throw new \Exception(printf("Node <%s> not found!", IN_PLACEMARK_NODE)); }

    // get location nodes
    $placemarks = $xml->{IN_DOCUMENT_NODE}->{IN_PLACEMARK_NODE};
    
    $locations = [];
    
    // parse every locations to convert coordinates from KML to WKT
    foreach ($placemarks as $p) {
        if (!property_exists($p, IN_NAME_NODE)) {
            printf("Placemark ignored due to missing <%s> (see below):\n", IN_NAME_NODE);
            print_r($p);
            print "\n";
            continue;
        }

        $name = trim($p->{IN_NAME_NODE}->__toString());

        $wkt = '';

        if (property_exists($p, IN_MULTIGEOMETRY_NODE) && property_exists($p->{IN_MULTIGEOMETRY_NODE}, IN_POLYGON_NODE)) {
            // multipolygon
            $r = kml2wkt($p->{IN_MULTIGEOMETRY_NODE}->{IN_POLYGON_NODE}, OUT_MULTIPOLYGON_HEADER, $wkt);
        } elseif (property_exists($p, IN_POLYGON_NODE)) {
            // polygon
            $r = kml2wkt($p->{IN_POLYGON_NODE}, OUT_POLYGON_HEADER, $wkt);
        } else {
            // non polygon
            printf("Placemark ignored due to missing <%s> (see below):\n", IN_POLYGON_NODE);
            print_r($p);
            print "\n";
            continue;
        }

        $l = new \stdClass();
        $l->{OUT_WKT_NODE} = $wkt;
        $l->{OUT_NAME_NODE} = $name;
        $l->{OUT_LOCALITY_NODE} = $locality;
        
        $locations[] = json_encode($l);
    }

    $xmlfileOut = $xmlfile . ".wkt.json";

    printf("Writing content to file %s\n", $xmlfileOut);
    file_put_contents($xmlfileOut, implode("\n", $locations));

    print "done.\n";

} catch (\Exception $e) {
    print "Conversion failed:\n";
    print $e->getMessage() . "\n";
}


function kml2wkt(\SimpleXMLElement $polygons, string $polygonType, string &$wkt): bool
{
    foreach ($polygons as $p) {
        // verify the expected format of the polygon
        if (!isValidPolygonNode($p)) { return false; }

        // build an array containing each coordinate pairs
        $cNode = $p->{IN_OUTERBOUNDARYIS_NODE}->{IN_LINEARRING_NODE}->{IN_COORDINATES_NODE}->__toString();
        $coordinates = explode("\n", $cNode);

        $wktCoordinates = [];
        foreach ($coordinates as $kc => $vc) {
            $vc = trim($vc);
            if ($vc == '') { continue; }

            // split lat and long
            $latLng = explode(',', $vc);

            // build the expected output coordinate
            $wktCoordinates[] = $latLng[0] . ' ' . $latLng[1];
        }

        $wktPolygons[] = '((' . implode(',', $wktCoordinates) . '))';
    }

    if ($polygonType == OUT_MULTIPOLYGON_HEADER) {
        // POLYGON ((-84.0728058 36.173027, ...))
        $wkt = $polygonType . ' (' . implode(',', $wktPolygons) . ')';
    } else {
        // MULTIPOLYGON (((-86.7712493 36.1977405, ...)))
        $wkt = $polygonType . ' ' . implode(',', $wktPolygons);
    }
    
    return true;
}

function isValidPolygonNode(\SimpleXMLElement $polygon): bool
{
    if (!property_exists($polygon, IN_OUTERBOUNDARYIS_NODE)) { return false; }
    if (!property_exists($polygon->{IN_OUTERBOUNDARYIS_NODE}, IN_LINEARRING_NODE)) { return false; }
    if (!property_exists($polygon->{IN_OUTERBOUNDARYIS_NODE}->{IN_LINEARRING_NODE}, IN_COORDINATES_NODE)) { return false; }

    return true;
}

