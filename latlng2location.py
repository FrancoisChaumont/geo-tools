#!/usr/bin/env python
import reverse_geocoder as rg
import smart_open
import sys
import json
import csv
import os

delimiter = '\t'

""" CUSTOMIZE HERE """
headers = [ \
    "lat", \
    "lng" \
]

""" replace null values by space """
def fixNulls(s):
    for line in s:
        yield line.replace('\0', ' ')

""" process """
def main(argv):
    try:
        input_data = sys.stdin
        csv.field_size_limit(sys.maxsize)
        csv_in = csv.DictReader(fixNulls(input_data), delimiter=delimiter, fieldnames=headers, quoting=csv.QUOTE_MINIMAL)

        """ load formatted geocoded file (preventing it to print <Loading formatted geocoded file...> to stdout) """
        sys.stdout = open(os.devnull, "w")
        rg.search((0, 0))
        sys.stdout = sys.__stdout__

        previousLat = 0
        previousLng = 0
        for line in csv_in:
            try:
                """ CUSTOMIZE HERE """
                lat = str(line['lat'])
                lng = str(line['lng'])

                if lat != previousLat or lng != previousLng:
                    r = rg.search((lat, lng))
                    latlng2country = r[0]['cc']

                """ CUSTOMIZE HERE """
                outline = '{}{}{}{}{}'.format( \
                    lat, \
                    delimiter, \
                    lng, \
                    delimiter, \
                    latlng2country \
                )

                print(outline)

                previousLat = lat
                previousLng = lng

            except:
                latlng2country = ''
                continue

    except EOFError:
        return None

    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)
