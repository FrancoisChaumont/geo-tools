import csv
import getopt
import io
import os
import sys

import geohash

lat_field_arg = ''
lng_field_arg = ''
field_separator = ''
print_headers = False
precision = 0
geohash_coordinates = False

def fixNulls(s):
    """ Replace null values by space """
    for line in s:
        yield line.replace('\0', ' ')

def init_options(argv):
    """ Verify and set up values from options/arguments """
    global lat_field_arg
    global lng_field_arg
    global field_separator
    global print_headers
    global precision
    global geohash_coordinates

    precision_arg = 0
    
    try:
        opts, args = getopt.getopt( \
            argv[1:], \
            "hl:L:d:p:og", \
            [ "help", "latitude=", "longitude=", "delimiter=", "precision=", "output-headers", "geohash-coordinates" ] \
        )

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                return False
            # MANDATORY ARGUMENTS
            elif opt in ("-l", "--latitude"):
                lat_field_arg = arg
            elif opt in ("-L", "--longitude"):
                lng_field_arg = arg
            elif opt in ("-d", "--delimiter"):
                field_separator = arg
            # OPTIONAL ARGUMENTS
            elif opt in ("-o", "--output-headers"):
                print_headers = True
            elif opt in ("-p", "--precision"):
                precision_arg = int(arg)
            elif opt in ("-g", "--geohash-coordinates"):
                geohash_coordinates = True

        if lat_field_arg == '' or lng_field_arg == '' or field_separator == '':
            raise Exception("Missing some mandatory fields!")
        if precision_arg < 1 and precision_arg != 0:
            raise Exception("Precision option must be superior to 0!")
        if precision_arg != 0:
            precision = precision_arg
        if field_separator == '':
            raise Exception("Field separator option cannot be empty!")

        return True

    except Exception as ex:
        raise Exception(ex)

def display_help(file_name):
    print("USAGE:")
    print(file_name)
    print("\t -h/--help                                                  Display usage help")
    print("")
    print("\t -l/--latitude=                <latitude field>             Field for latitude (column header/column index)")
    print("\t -L/--longitude=               <longitude field>            Field for longitude (column header/column index)")
    print("\t -d/--delimiter=               <field delimiter>            Field delimiter")
    print("\t[-p/--precision=]              <hash precision>             Precision of the geohash (starting at 1 and defaults to 12, ee README for details)")
    print("\t[-o/--output-headers]          <output headers>             Output headers (default: False), ignored if no headers present")
    print("\t[-g/--geohash-coordinates]     <geohash coordinates>        Append geohash coordinates (default: False)")
    print()
    print("EXAMPLE: no headers in input TSV data, output geohash precision of 6")
    print(f"cat examples/latlng2geohash/data-no-headers.tsv | python3 {file_name} -l 1 -L 2 -d $'\\t' -p 6 -g")
    print()
    print("EXAMPLE: headers in input CSV data but no headers in output")
    print(f"""cat examples/latlng2geohash/data-headers.csv | python3 {file_name} \\
        --latitude lat \\
        --longitude lng \\
        --delimiter , \\
        --precision 6 \\
        --geohash-coordinates
    """)

def geohashing(lat, lng, precision=0):
    """ Geohash lat lng """
    if precision != 0:
        gh = geohash.encode( \
            lat, \
            lng, \
            precision=precision \
        )
    else:
        gh = geohash.encode( \
            lat, \
            lng \
        )

    if geohash_coordinates:
        gc = geohash.decode( \
            gh
        )
        return gh, gc
    else:
        return gh

def output_data(has_headers, line_fields, geohash='', lat=0, lng=0):
    global field_separator

    """ Output data """
    if has_headers:
        if geohash_coordinates:
            print(f"{field_separator.join(line_fields.values())}{field_separator}{geohash}{field_separator}{lat}{field_separator}{lng}")
        else:
            print(f"{field_separator.join(line_fields.values())}{field_separator}{geohash}")
    else:
        if geohash_coordinates:
            print(f"{field_separator.join(line_fields)}{field_separator}{geohash}{field_separator}{lat}{field_separator}{lng}")
        else:
            print(f"{field_separator.join(line_fields)}{field_separator}{geohash}")

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
            lat_field = int(lat_field_arg) - 1
            lng_field = int(lng_field_arg) - 1

            # geohash first lines
            line_fields = csv.reader(first_line.splitlines(), delimiter=field_separator, quoting=csv.QUOTE_MINIMAL).__next__()
            if geohash_coordinates:
                geohash, coordinates = geohashing(float(line_fields[lat_field]), float(line_fields[lng_field]), precision)
                output_data(has_headers, line_fields, geohash, coordinates[0], coordinates[1])
            else:
                geohash = geohashing(float(line_fields[lat_field]), float(line_fields[lng_field]), precision)
                output_data(has_headers, line_fields, geohash)
            
            # geohash second line
            line_fields = csv.reader(second_line.splitlines(), delimiter=field_separator, quoting=csv.QUOTE_MINIMAL).__next__()
            if geohash_coordinates:
                geohash, coordinates = geohashing(float(line_fields[lat_field]), float(line_fields[lng_field]), precision)
                output_data(has_headers, line_fields, geohash, coordinates[0], coordinates[1])
            else:
                geohash = geohashing(float(line_fields[lat_field]), float(line_fields[lng_field]), precision)
                output_data(has_headers, line_fields, geohash)

            # init CSV reader
            reader = csv.reader(fixNulls(input_data), delimiter=field_separator, quoting=csv.QUOTE_MINIMAL)

        else:
            # field headers
            lat_field = lat_field_arg
            lng_field = lng_field_arg

            # retrieve all headers
            headers = csv.reader(first_line.splitlines(), delimiter=field_separator, quoting=csv.QUOTE_MINIMAL).__next__()
            
            # generate output headers
            if print_headers:
                output_headers = headers.copy()
                output_headers.append('geohash')
                if geohash_coordinates:
                    output_headers.append('geohash_lat')
                    output_headers.append('geohash_lng')
                print(f"{field_separator.join(output_headers)}")

            # geohash second line
            line_fields = csv.DictReader(second_line.splitlines(), delimiter=field_separator, fieldnames=headers, quoting=csv.QUOTE_MINIMAL).__next__()
            if geohash_coordinates:
                geohash, coordinates = geohashing(float(line_fields[lat_field]), float(line_fields[lng_field]), precision)
                output_data(has_headers, line_fields, geohash, coordinates[0], coordinates[1])    
            else:
                geohash = geohashing(float(line_fields[lat_field]), float(line_fields[lng_field]), precision)
                output_data(has_headers, line_fields, geohash)

            # init CSV reader
            reader = csv.DictReader(fixNulls(input_data), delimiter=field_separator, fieldnames=headers, quoting=csv.QUOTE_MINIMAL)
        
        # geohash other lines
        previous_lat = 0
        previous_lng = 0
        for line_fields in reader:
            try:
                lat = float(line_fields[lat_field])
                lng = float(line_fields[lng_field])

                # geohash
                if lat != previous_lat or lng != previous_lng:
                    if geohash_coordinates:
                        geohash, coordinates = geohashing(lat, lng, precision)
                    else:
                        geohash = geohashing(lat, lng, precision)
                
                # output line + geohash appended
                if geohash_coordinates:
                    output_data(has_headers, line_fields, geohash, coordinates[0], coordinates[1])
                else:
                    output_data(has_headers, line_fields, geohash)

                previous_lat = lat
                previous_lng = lng

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
