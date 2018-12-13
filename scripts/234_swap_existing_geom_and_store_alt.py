#stepps00 - 12-12-2018
#used to swap out buffered point geometries

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

            if feature:
                props = feature['properties']
                geom =  feature['geometry']

                found = False

                #by now, we've read in the feature and mapped the geom and props for later use
                #check if the geometry is from Quattroshapes
                if props['src:geom'] == 'quattroshapes':

                    #if it is, map existing lat/long values to a new Point geometry
                    if not found:
                        if props.has_key('lbl:latitude'):
                            if props.has_key('lbl:longitude'):
                                lat = props['lbl:latitude']
                                long = props['lbl:longitude']
                                found = True

                    if not found:
                        if props.has_key('mps:latitude'):
                            if props.has_key('mps:longitude'):
                                lat = props['mps:latitude']
                                long = props['mps:longitude']
                                found = True

                    if not found:
                        if props.has_key('geom:latitude'):
                            if props.has_key('geom:longitude'):
                               lat = props['geom:latitude']
                               long = props['geom:longitude']
                               found = True

                    #if we've created a new lat/long mapping...
                    if found:
                        #give record a new Point geom
                        feature['geometry'] = {"coordinates":[float(long),float(lat)],"type":"Point"}

                        #update src properties
                        props['src:geom'] = 'whosonfirst'
                        props['src:geom_via'] = 'quattroshapes'

                        if props.has_key('src:geom_alt'):
                            props['src:geom_alt'].append('quattroshapes')

                        if not props.has_key('src:geom_alt'):
                            props['src:geom_alt'] = ['quattroshapes']

                        #create a new Quattroshapes alt file
                        alt_geom = {'type': 'Feature'}
                        alt_geom['properties'] = {
                            'wof:id': props.get('wof:id'),
                            'src:geom': 'quattroshapes'
                        }

                        #and use old geom variable as new alt geom, export
                        alt_geom['geometry'] = geom

                        exporter.export_alt_feature(alt_geom, alt=alt_geom['properties']['src:geom'])
                        exporter.export_feature(feature)
                        #print feature
                        #print alt_geom

                    #hopefully we don't get here...
                    if not found:
                        print '\t\tNOT FOUND:' + str(id)
