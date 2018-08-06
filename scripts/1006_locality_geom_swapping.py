#stepps00 07.16.2018

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
        iso_country = row['iso_country']
        wof_country = row['wof_country']

        if id:
            feature = mapzen.whosonfirst.utils.load(source, id)

            if feature:

                tier = False
                src_check = False
                is_us = False

                props = feature['properties']
                geom = feature['geometry']

                if not geom['type'] == 'Point':
                    if props.has_key('src:geom'):
                        geom_src = props['src:geom']

                    #only operate on qs and as geom records
                    if props.has_key('src:geom'):
                        if props['src:geom'] == 'zetashapes':
                            src_check = True

                    if src_check:
                        #also check if the feature is in the US
                        if iso_country == 'US':
                            is_us = True
                        if wof_country == 'US':
                            is_us = True

                        if is_us:
                            #this assumes the placetype is microhood, macrohood, or neighbourhood
                            #if tier locality is 3/2/1 or if that's not defined at all, iterate over feature
                            if props.has_key('mz:tier_locality'):
                                if props['mz:tier_locality'] == 1:
                                    tier = True
                                if props['mz:tier_locality'] == 2:
                                    tier = True
                                if props['mz:tier_locality'] == 3:
                                    tier = True
                            else:
                                 tier = True

                            if tier: 
                                #set hierarchy label
                                props['mz:hierarchy_label'] = 0

                                #also, swap lbl lat long as geo
                                if props.has_key('geom:latitude'):
                                    lat = props['geom:latitude']
                                if props.has_key('geom:longitude'):
                                    long = props['geom:longitude']

                                #use geom, unless we have lbl...
                                if props.has_key('lbl:latitude'):
                                    lat = props['lbl:latitude']
                                if props.has_key('lbl:longitude'):
                                    long = props['lbl:longitude']

                                #construct new point geometry
                                feature['geometry'] = {"coordinates":[long,lat],"type":"Point"}
                                props['src:geom'] = 'mz'

                                #and save geom as alt
                                if not props.has_key('src:geom_alt'):
                                    props['src:geom_alt'] = [geom_src]
                                else:
                                    props['src:geom_alt'].append(geom_src)

                                #create the alt file, map the id and props
                                alt_geom = {'type': 'Feature'}
                                alt_geom['properties'] = {
                                    'wof:id': props.get('wof:id'),
                                    'src:geom': geom_src
                                }

                                #use old geom variable as new alt geom, export
                                alt_geom['geometry'] = geom
                                exporter.export_alt_feature(alt_geom, alt=alt_geom['properties']['src:geom'])

                                #and export the default file
                                exporter.export_feature(feature)
                                print 'done with ' + str(props['wof:id'])