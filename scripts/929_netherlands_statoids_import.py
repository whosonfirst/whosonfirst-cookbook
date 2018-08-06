#stepps00 - 04.2018
#import statoids data

import sys
import os
import logging
import optparse
import csv
import json
import geojson
import pprint
import mapzen.whosonfirst.utils
import mapzen.whosonfirst.placetypes
import mapzen.whosonfirst.export

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':

    opt_parser = optparse.OptionParser()
    opt_parser.add_option('-i', '--input', dest='input', action='store', default=None, help='Where to read CSV import file from')
    opt_parser.add_option('-o', '--output', dest='output', action='store', default="/path/to/whosonfirst-data/data", help='Where to write WOF records to')
    options, args = opt_parser.parse_args()

    # CSV file to process
    places = options.input
    fh = open(places, 'r')
    source = os.path.abspath(options.output)
    exporter = mapzen.whosonfirst.export.flatfile(source)

    # start processing the records to deprecate
    reader = csv.DictReader(fh)

    for row in reader:
        id = row['id']
        name = row['name']
        country = row['country']
        timezone = row['timezone']
        hasc = row['hasc']
        iso = row['iso']
        gec = row['gec']
        type = row['type']
        population = row['population']
        date = row['date']
        areakm = row['area-km']
        areami = row['area-mi']
        capital = row['capital']

        # load the WOF record
        # guard against null values in CSV
        if id:
            feature = mapzen.whosonfirst.utils.load(source, id)

            # guard against bogus WOF ids not matching any feature
            if feature:
                props = feature['properties']

                #we know this record is current
                props['mz:is_current'] = 1

                #read in each statoid property explicitly
                props['statoids:name'] = name
                props['statoids:country'] = country
                props['statoids:timezone'] = timezone
                props['statoids:hasc'] = hasc
                props['statoids:iso'] = iso
                props['statoids:gec'] = gec
                props['statoids:type'] = type
                props['statoids:population'] = population
                props['statoids:as_of_date'] = date
                props['statoids:area_km'] = areakm
                props['statoids:area_mi'] = areami
                props['statoids:capital'] = capital

                #pull out concordances to add hasc:id
                concordances = props['wof:concordances']
                concordances['hasc:id'] = hasc
                props['wof:concordances'] = concordances

                #be chatty, export changes
                exporter.export_feature(feature)
                print id + ' is done.'

            else:
                print 'No feature.'
        else:
        	print 'Not a valid id.'