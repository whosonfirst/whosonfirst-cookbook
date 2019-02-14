#check parent records in AU neighbourhoods
#stepps00 - 2019-02-14

import osgeo.ogr

import sys
import os
import logging
import optparse
import csv
import pprint
import datetime
import mapzen.whosonfirst.utils
import mapzen.whosonfirst.placetypes
import mapzen.whosonfirst.export
import json
import geojson

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

            #we have a feature
            if feature:
                props = feature['properties']

                #only operate on current records, guard against weirdness
                is_current = -1
                if props.has_key('mz:is_current'):
                    is_current = props['mz:is_current']

                #if we have a current record...
                if not int(is_current) == 0:
                    #check all hierarchies
                    for item in props['wof:hierarchy']:
                        #check all pairs in hierarchy
                        for k,v in item.items():
                            if k == 'locality_id':
                                #if we have a locality id (that isnt -1)
                                if not v == -1:
                                    #load it and check properties
                                    parent_feature = mapzen.whosonfirst.utils.load(source, v)

                                    if parent_feature:
                                        if str(feature['properties']['wof:name']) in str(parent_feature['properties']['wof:name']):
                                            print str(id) + ' ' + str(parent_feature['properties']['wof:id'])

                                        if not str(feature['properties']['wof:name']) in str(parent_feature['properties']['wof:name']):
                                            print str(id) + ' does not match.'
