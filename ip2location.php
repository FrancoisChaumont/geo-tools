<?php

ini_set('memory_limit', '-1');
ini_set("display_errors", true);
ini_set("error_reporting", E_ALL);

require_once __DIR__ . '/ip2location.usage.php';
require_once __DIR__ . '/vendor/autoload.php';

try {
    // initialization of the parameters
    if (isset($options['input'])) {
        $source = $options['input'];
        if (!is_readable($source)) { throw new \Exception("Input file not found or readable!"); }
    }
    else { throw new \Exception("Missing <input> argument!"); }
    
    if (isset($options['ip'])) {
        $ipfield = intval($options['ip']);
        if ($ipfield == 0) { throw new \Exception("Invalid value for argument <ip>!"); }
    }
    else { $ipfield = 1; }
    $ipfield -= 1; // 0 based for array index

    if (isset($options['output'])) { $destination = $options['output']; }
    else { throw new \Exception("Missing <output> argument!"); }

    if (isset($options['delimiter'])) { $delimiter = $options['delimiter']; } 
    else { $delimiter = "\t"; }

    if (isset($options['database'])) { $delimiter = $options['database']; } 
    else { $database = __DIR__ . '/databases/GeoLite2-City.mmdb'; }

    $discardNoState = isset($options['discard-no-us-states']);
    $keepAllStates = isset($options['keep-all-states']);
    $countryOnly = isset($options['country-only']);

    // initialize GeoIp database reader
    $reader = new \GeoIp2\Database\Reader($database, ['en'], true);

    // load whole input file to memory
    echo "Loading input file to memory\n";
    $memfile = 'php://memory';
    $memfin = new \SplFileObject($memfile, 'w+');
    $memfin->fwrite(file_get_contents($source));
    
    echo "Reading data from memory\n";
    $memfin->rewind();
    $memfin->setFlags(\SPLFileObject::SKIP_EMPTY | \SPLFileObject::DROP_NEW_LINE | \SplFileObject::READ_AHEAD | \SplFileObject::READ_CSV);
    $memfin->setCsvControl($delimiter);

    $content = '';

    echo "Parsing data\n";
    $previousIp = -1;
    foreach ($memfin as $rawsources) {
        $ip = $rawsources[$ipfield];

        if ($previousIp != $ip) {
            $state = '';
            $country = '';

            if (filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)) {
                try {
                    $record = $reader->city($ip); // throw an exception if not found

                    $country = strtoupper($record->country->isoCode);
                    $state = strtoupper($record->mostSpecificSubdivision->isoCode);

                    $country = preg_match('/^[A-Z]{2}$/', $country) == 1 ? $country : '';
                    $state = !$keepAllStates && $country != 'US' || preg_match('/^[A-Z]{2}$/', $state) != 1 ? '' : $state;

                    if (empty($state) && $discardNoState) {
                        $country = '';
                        $state = '';
                    }
                } catch (\Exception $e) {
                    $state = '';
                    $country = '';
                }
            }
        }

        if ($countryOnly) {
            $content .= implode($delimiter, $rawsources) . $delimiter . strtoupper($country) . PHP_EOL;
        } else {
            $content .= implode($delimiter, $rawsources) . $delimiter . strtoupper($country) . $delimiter . strtoupper($state) . PHP_EOL;
        }

        $previousIp = $ip;
    }

    // write content to file
    echo "Writing content to output file\n";
    file_put_contents($destination, $content);

} catch (\Exception $e) {
    print $e->getMessage() . PHP_EOL;
}

echo "Done.\n";
