#stepps00 - 07-25-2018
#used to update Township names

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

    places = options.input
    fh = open(places, 'r')
    source = os.path.abspath(options.output)
    exporter = mapzen.whosonfirst.export.flatfile(source)
    reader = csv.DictReader(fh)

    for row in reader:
        id = row['id']

        if id:
            feature = mapzen.whosonfirst.utils.load(source, id)

            change = False

            if feature:
                props = feature['properties']

                #input csv should only have twp types, but make sure
                if props['qs:type'] == 'twp':

                    #they should also have wof:names, but make sure
                    if props.has_key('wof:name'):
                        #construct new name variable
                        township_name = str(props['wof:name']) + ' Township'

                        #if variant namespace exists..
                        if props.has_key('name:eng_x_variant'):
                            #add existing name as variant
                            props['name:eng_x_variant'].append(props['wof:name'])

                            sanitized_variants = []

                            for name in props['name:eng_x_variant']:
                                #scrub names..
                                if not name in sanitized_variants:
                                    sanitized_variants.append(name)

                            #then.. remap all props
                            props['name:eng_x_variant'] = sanitized_variants
                            props['name:eng_x_preferred'] = [township_name]
                            props['wof:name'] = township_name
                            change = True

                        #if no variant namespace, then simply move mappings around
                        else:
                            props['name:eng_x_variant'] = [props['wof:name']]
                            props['name:eng_x_preferred'] = [township_name]
                            props['wof:name'] = township_name
                            change = True

                    else:
                        str(id) + 'has no name; SKIPPING'

                else:
                    print str(id) + ' does not have a township qs type, SKIPPING'

            #write
            if change:
                exporter.export_feature(feature)
                print str(props['wof:id']) + ' is done.'