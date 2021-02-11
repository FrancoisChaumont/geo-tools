import csv
import getopt
import io
import os
import sys
import numpy as np

lat1_field_arg = ''
lng1_field_arg = ''
lat2_field_arg = ''
lng2_field_arg = ''
field_separator = ''
print_headers = False
convert_to_miles = False

def fixNulls(s):
    """ Replace null values by space """
    for line in s:
        yield line.replace('\0', ' ')

def init_options(argv):
    """ Verify and set up values from options/arguments """
    global lat1_field_arg
    global lng1_field_arg
    global lat2_field_arg
    global lng2_field_arg
    global field_separator
    global print_headers
    global convert_to_miles
    
    try:
        opts, args = getopt.getopt( \
            argv[1:], \
            "hl:L:m:M:d:oc", \
            [ "help", "latitude1=", "longitude1=", "latitude2=", "longitude2=", "delimiter=", "output-headers", "convert-to-miles" ] \
        )

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                return False
            # MANDATORY ARGUMENTS
            elif opt in ("-l", "--latitude1"):
                lat1_field_arg = arg
            elif opt in ("-L", "--longitude1"):
                lng1_field_arg = arg
            elif opt in ("-m", "--latitude2"):
                lat2_field_arg = arg
            elif opt in ("-M", "--longitude2"):
                lng2_field_arg = arg
            elif opt in ("-d", "--delimiter"):
                field_separator = arg
            # OPTIONAL ARGUMENTS
            elif opt in ("-o", "--output-headers"):
                print_headers = True
            elif opt in ("-c", "--convert-to-miles"):
                convert_to_miles = True

        if lat1_field_arg == '' or lng1_field_arg == '' or lat2_field_arg == '' or lng2_field_arg == '' or field_separator == '':
            raise Exception("Missing some mandatory fields!")
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
    print("\t -l/--latitude1=               <latitude1 field>            Field for latitude1 (column header/column index)")
    print("\t -L/--longitude1=              <longitude1 field>           Field for longitude1 (column header/column index)")
    print("\t -m/--latitude2=               <latitude2 field>            Field for latitude2 (column header/column index)")
    print("\t -M/--longitude2=              <longitude3 field>           Field for longitude2 (column header/column index)")
    print("\t -d/--delimiter=               <field delimiter>            Field delimiter")
    print("\t[-o/--output-headers]          <output headers>             Output headers (default: False), ignored if no headers present")
    print("\t[-c/--convert-to-miles]        <convert to miles>           Output miles instead of km (default: False)")
    print()
    print("EXAMPLE: no headers in input TSV data, output in km")
    print(f"cat examples/latlng2distance/data-no-headers.tsv | python3 {file_name} -l 2 -L 3 -m 4 -M 5 -d $'\\t'")
    print()
    print("EXAMPLE: headers in input CSV data and in output, output in miles")
    print(f"""cat examples/latlng2distance/data-headers.csv | python3 {file_name} \\
        --latitude1 lat1 \\
        --longitude1 lng1 \\
        --latitude2 lat2 \\
        --longitude2 lng2 \\
        --delimiter , \\
        --output-headers \\
        --convert-to-miles
    """)

def haversine_distance(lat1, lng1, lat2, lng2, convert_to_miles):
    """ Calculate Haversine distance in km/miles between 2 pairs of coordinates """
    if lat1 == lat2 and lng1 == lng2:
        return 0
    
    r = 6371
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    delta_phi = np.radians(lat2 - lat1)
    delta_lambda = np.radians(lng2 - lng1)
    a = np.sin(delta_phi / 2)**2 + np.cos(phi1) * np.cos(phi2) *   np.sin(delta_lambda / 2)**2
    res = r * (2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a)))

    if convert_to_miles:
        res = res * 0.62137119

    return np.round(res, 2)

def output_data(has_headers, line_fields, distance=0):
    global field_separator
    
    """ Output data """
    if has_headers:
        print(f"{field_separator.join(line_fields.values())}{field_separator}{distance}")
    else:
        print(f"{field_separator.join(line_fields)}{field_separator}{distance}")

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
            lat1_field = int(lat1_field_arg) - 1
            lng1_field = int(lng1_field_arg) - 1
            lat2_field = int(lat2_field_arg) - 1
            lng2_field = int(lng2_field_arg) - 1

            # distance first lines
            line_fields = csv.reader(first_line.splitlines(), delimiter=field_separator, quoting=csv.QUOTE_MINIMAL).__next__()
            distance = haversine_distance( \
                float(line_fields[lat1_field]), \
                float(line_fields[lng1_field]), \
                float(line_fields[lat2_field]), \
                float(line_fields[lng2_field]), \
                convert_to_miles \
            )
            output_data(has_headers, line_fields, distance)
            
            # distance second line
            line_fields = csv.reader(second_line.splitlines(), delimiter=field_separator, quoting=csv.QUOTE_MINIMAL).__next__()
            distance = haversine_distance( \
                float(line_fields[lat1_field]), \
                float(line_fields[lng1_field]), \
                float(line_fields[lat2_field]), \
                float(line_fields[lng2_field]), \
                convert_to_miles \
            )
            output_data(has_headers, line_fields, distance)

            # init CSV reader
            reader = csv.reader(fixNulls(input_data), delimiter=field_separator, quoting=csv.QUOTE_MINIMAL)

        else:
            # field headers
            lat1_field = lat1_field_arg
            lng1_field = lng1_field_arg
            lat2_field = lat2_field_arg
            lng2_field = lng2_field_arg

            # retrieve all headers
            headers = csv.reader(first_line.splitlines(), delimiter=field_separator, quoting=csv.QUOTE_MINIMAL).__next__()
            
            # generate output headers
            if print_headers:
                output_headers = headers.copy()
                output_headers.append('distance')
                print(f"{field_separator.join(output_headers)}")

            # distance second line
            line_fields = csv.DictReader(second_line.splitlines(), delimiter=field_separator, fieldnames=headers, quoting=csv.QUOTE_MINIMAL).__next__()
            distance = haversine_distance( \
                float(line_fields[lat1_field]), \
                float(line_fields[lng1_field]), \
                float(line_fields[lat2_field]), \
                float(line_fields[lng2_field]), \
                convert_to_miles \
            )
            output_data(has_headers, line_fields, distance)

            # init CSV reader
            reader = csv.DictReader(fixNulls(input_data), delimiter=field_separator, fieldnames=headers, quoting=csv.QUOTE_MINIMAL)
        
        # distance other lines
        previous_lat1 = 0
        previous_lng1 = 0
        previous_lat2 = 0
        previous_lng2 = 0
        for line_fields in reader:
            try:
                lat1 = float(line_fields[lat1_field])
                lng1 = float(line_fields[lng1_field])
                lat2 = float(line_fields[lat2_field])
                lng2 = float(line_fields[lng2_field])

                # distance
                if lat1 != previous_lat1 or lng1 != previous_lng1 or lat2 != previous_lat2 or lng2 != previous_lng2:
                    distance = haversine_distance(lat1, lng1, lat2, lng2, convert_to_miles)
                
                # output line + distance appended
                output_data(has_headers, line_fields, distance)

                previous_lat1 = lat1
                previous_lng1 = lng1
                previous_lat2 = lat2
                previous_lng2 = lng2

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
