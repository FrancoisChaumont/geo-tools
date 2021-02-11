<?php

/**
 * INCLUDE THIS FILE IN YOUR MAIN ENTRY POINT SCRIPT
 */

// retrieve the name of the file that includes this file
define('INCLUDED_FILE', basename(get_included_files()[0]));

// modify the description here below
define('USAGE', sprintf("Usage: php %s %s\n", INCLUDED_FILE, <<<EOS
[options]

Options:
    --help                                      Show this help message and exit

    --input=path-to-input-file                  Path to the input file containing the IP to match with
    --output=path-to-output-file                Path to the output file
    --delimiter=input/output-field-delimiter    [OPTIONAL] Field delimiter for the input/output file
                                                If not provided, it defaults to a tabulation

    --ip=input-file-ip-field                    [OPTIONAL] IP field # in file
                                                If not provided, it defaults to 1

    --database=path-to-the-database-file        [OPTIONAL] Path to the database file
                                                If not provided, it defaults to <GeoLite2-City.mmdb> located under the directory <databases>

    --discard-no-us-states                      [OPTIONAL] Discard US country without a state
                                                If provided, US country without a state will be output as not found (no country, no state)
                                                If not provided, US country without a state will be output as is (US with an empty state)

    --keep-all-states                           [OPTIONAL] Keep states other than US
                                                If not provided, only US states will be output

    --country-only                              [OPTIONAL] Append country only, no state
                                                If not provided, country and state will be output

Usage:
    php ip2location.php --input=INPUT_FILE --output=OUTPUT_FILE [--delimiter=,] [--ip=1] [--database=DATABASE.mmdb] [--discard-no-us-state] [--keep-all-states] [--country-only]
EOS
));

$shortOpts = null;
$longOpts = [
    'help',
    'input:',
    'output:',
    'delimiter:',
    'ip:',
    'database:',
    'discard-no-us-states',
    'keep-all-states',
    'country-only'
];

// set options for this run
$options = getopt($shortOpts, $longOpts);
if (isset($options['help'])) {
    print USAGE;
    exit;
}

