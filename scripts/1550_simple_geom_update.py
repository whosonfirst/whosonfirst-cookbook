#stepps00 - 2020-07-15
#simply update geoms from featurecollection

import sys
import os
import logging
import optparse
import json
import geojson
import mapzen.whosonfirst.utils
import mapzen.whosonfirst.placetypes
import mapzen.whosonfirst.export

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':

    opt_parser = optparse.OptionParser()

    opt_parser.add_option('-i', '--input', dest='input', action='store', default=None, help='Where to read GeoJSON import file from')
    opt_parser.add_option('-o', '--output', dest='output', action='store', default="/path/to/data", help='Where to write WOF records to')

    options, args = opt_parser.parse_args()

    fh = open(options.input, 'r')
    output = os.path.abspath(options.output)
    exporter = mapzen.whosonfirst.export.flatfile(output)

    #read in the entire geojson collection
    collection = geojson.load(fh)

    #but iterate over each feature uniquely
    for feature in collection['features']:

        #create variables for new props and geom in input file
        new_props = feature['properties']
        new_geom = feature['geometry']

        id = new_props['id']

        feature = mapzen.whosonfirst.utils.load(output, id)

        if feature:

            #update geom
            feature['geometry'] = new_geom

            exporter.export_feature(feature)
