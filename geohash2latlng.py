import csv
import getopt
import io
import os
import sys

import geohash

geo_field_arg = ''
field_separator = ''
print_headers = False

def fixNulls(s):
    """ Replace null values by space """
    for line in s:
        yield line.replace('\0', ' ')

def init_options(argv):
    """ Verify and set up values from options/arguments """
    global geo_field_arg
    global field_separator
    global print_headers
    
    try:
        opts, args = getopt.getopt( \
            argv[1:], \
            "hg:d:o", \
            [ "help", "geohash=", "delimiter=", "output-headers" ] \
        )

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                return False
            # MANDATORY ARGUMENTS
            elif opt in ("-g", "--geohash"):
                geo_field_arg = arg
            elif opt in ("-d", "--delimiter"):
                field_separator = arg
            # OPTIONAL ARGUMENTS
            elif opt in ("-o", "--output-headers"):
                print_headers = True

        if geo_field_arg == '' or field_separator == '':
            raise Exception("Missing some mandatory fields!")
        if field_separator == '':
            raise Exception("Field separator option cannot be empty!")

        return True

    except Exception as ex:
        raise Exception(ex)

def display_help(file_name):
    print("USAGE:")
    print(file_name)
    print("\t -h/--help                                             Display usage help")
    print("")
    print("\t -g/--geohash=            <geohash field>              Field for geohash (column header/column index)")
    print("\t -d/--delimiter=          <field delimiter>            Field delimiter")
    print("\t[-o/--output-headers]     <output headers>             Output headers (default: False), ignored if no headers present")
    print()
    print("EXAMPLE: no headers in input TSV data, output lat/lng")
    print(f"cat examples/geohash2latlng/data-no-headers.tsv | python3 {file_name} -g 1 -d $'\\t'")
    print()
    print("EXAMPLE: headers in input CSV data but no headers in output")
    print(f"""cat examples/geohash2latlng/data-headers.csv | python3 {file_name} \\
        --geohash geohash \\
        --delimiter ,
    """)

def decode_geohash(geo):
    """ Decode geohash into Lat/Lng coordinates """
    coordinates = geohash.decode( \
        geo \
    )

    return coordinates

def output_data(has_headers, line_fields, lat=0, lng=0):
    global field_separator

    """ Output data """
    if has_headers:
        print(f"{field_separator.join(line_fields.values())}{field_separator}{lat}{field_separator}{lng}")
    else:
        print(f"{field_separator.join(line_fields)}{field_separator}{lat}{field_separator}{lng}")

def main(argv):
    """ Process """
    try:
        csv.field_size_limit(sys.maxsize)

        # retrieve arguments
        if not init_options(argv):
            display_help(os.path.basename(__file__))
            return

        # output to stdout
        sys.stdout = open(os.devnull, "w")
        sys.stdout = sys.__stdout__

        # input from sdtin
        input_data = sys.stdin

        # look for headers
        first_line = input_data.readline().strip('\n')
        second_line = input_data.readline().strip('\n')
        if first_line == '' or second_line == '':
            raise Exception("Input must be 2 lines long or more!")
        has_headers = csv.Sniffer().has_header(f"{first_line}\n{second_line}\n")

        if not has_headers:
            # field indexes
            geo_field = int(geo_field_arg) - 1

            # decode geohash first lines
            line_fields = csv.reader(first_line.splitlines(), delimiter=field_separator, quoting=csv.QUOTE_MINIMAL).__next__()
            coordinates = decode_geohash(line_fields[geo_field])
            output_data(has_headers, line_fields, coordinates[0], coordinates[1])
            
            # decode geohash second line
            line_fields = csv.reader(second_line.splitlines(), delimiter=field_separator, quoting=csv.QUOTE_MINIMAL).__next__()
            coordinates = decode_geohash(line_fields[geo_field])
            output_data(has_headers, line_fields, coordinates[0], coordinates[1])

            # init CSV reader
            reader = csv.reader(fixNulls(input_data), delimiter=field_separator, quoting=csv.QUOTE_MINIMAL)

        else:
            # field headers
            geo_field = geo_field_arg

            # retrieve all headers
            headers = csv.reader(first_line.splitlines(), delimiter=field_separator, quoting=csv.QUOTE_MINIMAL).__next__()
            
            # generate output headers
            if print_headers:
                output_headers = headers.copy()
                output_headers.append('lat')
                output_headers.append('lng')
                print(f"{field_separator.join(output_headers)}")

            # decode geohash second line
            line_fields = csv.DictReader(second_line.splitlines(), delimiter=field_separator, fieldnames=headers, quoting=csv.QUOTE_MINIMAL).__next__()
            coordinates = decode_geohash(line_fields[geo_field])
            output_data(has_headers, line_fields, coordinates[0], coordinates[1])

            # init CSV reader
            reader = csv.DictReader(fixNulls(input_data), delimiter=field_separator, fieldnames=headers, quoting=csv.QUOTE_MINIMAL)
        
        # decode geohash for other lines
        previous_geo = ''
        for line_fields in reader:
            try:
                geo = line_fields[geo_field]

                # geohash
                if geo != previous_geo:
                    coordinates = decode_geohash(geo)
                
                # output line + geohash appended
                output_data(has_headers, line_fields, coordinates[0], coordinates[1])

                previous_geo = geo

            except EOFError:
                return None

            except Exception:
                output_data(has_headers, line_fields)

    except Exception as ex:
        print(f"Failed: {ex}")
        sys.exit(1)

if __name__ == '__main__':
    main(sys.argv)
    sys.exit(0)
