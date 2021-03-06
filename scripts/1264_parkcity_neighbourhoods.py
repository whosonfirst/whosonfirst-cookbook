#stepps00 2018.06.07

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

    opt_parser.add_option('-i', '--input', dest='input', action='store', default=None, help='Where to read GeoJSON import file from')
    opt_parser.add_option('-o', '--output', dest='output', action='store', default="/path/to/whosonfirst-data/data", help='Where to write WOF records to')

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

        #read in id and concordances explicitly
        id    = new_props['id']
        name  = new_props['name']

        #read in lat/long vals
        latitude = new_props['latitude']
        longitude = new_props['longitude']

        #we're not loading in a new feature, we're creating one from scratch this time...
        feature = {
            "id":          id,
            "type":        "Feature",
            "properties":  {},
            "bbox":        {},
            "geometry":    {}
        }

        #create variables for existing props and geom to store later (geom moves to alt)
        props = feature['properties']
        geom = feature['geometry']

        #we vrified these are all current, so flag
        props['mz:is_current'] = 1

        #give new names
        props['wof:name'] = name
        props['name:eng_x_preferred'] = [name]

        #set parent
        props['wof:parent_id'] = -1

        #wof id
        props['wof:id'] = id

        #iso and wof country codes
        props['wof:country'] = 'US'
        props['iso:country'] = 'US'

        #langs
        props['wof:lang_x_spoken'] = ['eng']
        props['wof:lang_x_official'] = ['eng']

        #placetype
        props['wof:placetype'] = 'neighbourhood'

        #geom src
        props['src:geom'] = 'mz'

        #lbl and mps lat/longs
        props['mps:latitude'] = latitude
        props['mps:longitude'] = longitude
        props['lbl:latitude'] = latitude
        props['lbl:longitude'] = longitude

        #map new props and geom and export default feature
        feature['properties'] = props
        feature['geometry'] = new_geom

        exporter.export_feature(feature)
        #be chatty
        print str(props['wof:id']) + ' is done.'