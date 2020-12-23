#stepps00 2018.05.25
#update HK region records

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
    opt_parser.add_option('-s', '--source', dest='wof_source', action='store', default=None, help='What WOF data source identifier')
    options, args = opt_parser.parse_args()

    fh = open(options.input, 'r')
    output = os.path.abspath(options.output)
    exporter = mapzen.whosonfirst.export.flatfile(output)
    collection = geojson.load(fh)

    #but iterate over each feature uniquely
    for feature in collection['features']:

        #create variables for new props and geom in input file
        new_props = feature['properties']
        new_geom = feature['geometry']

        #read in the statoids properties explicitly
        if new_props.has_key('name_en'):
            name_eng = new_props['name_en']

        if new_props.has_key('name_chi'):
            name_chi = new_props['name_chi']

        if new_props.has_key('id'):
            id = new_props['id']

        if id:
            feature = mapzen.whosonfirst.utils.load(output, id)

            # guard against bogus WOF ids not matching any feature
            if feature:
                #create variables for existing props and geom to store later (geom moves to alt)
                props = feature['properties']
                geom = feature['geometry']

                #eng name
                if not name_eng == props['wof:name']:
                    existing_wof_name = props['wof:name']
                    props['wof:name'] = name_eng

                    if props.has_key('name:eng_x_preferred'):
                        props['name:eng_x_preferred'] = props['wof:name']
                        if props.has_key('name:eng_x_variant'):
                            if not existing_wof_name in props['name:eng_x_variant']:
                                props['name:eng_x_variant'].append(existing_wof_name)

                    else:
                        props['name:eng_x_variant'] = existing_wof_name

                #chi name
                if not props.has_key('name:zho_x_preferred'):
                    props['name:zho_x_preferred'] = [name_chi]

                else:
                    if not name_chi in props['name:zho_x_preferred']:
                        if not props.has_key('name:zho_x_variant'):
                            props['name:zho_x_variant'] = [name_chi]

                        else:
                            props['name:zho_x_variant'].append(name_chi)

                #we are updating, therefore current
                props['mz:is_current'] = 1

                #store new geom as default geom, create alt geom file and map src geom props
                geom_src = props['src:geom']
                props['src:geom'] = 'hk-gov'

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
                alt_geom['geometry'] = feature['geometry']
                exporter.export_alt_feature(alt_geom, alt=alt_geom['properties']['src:geom'])

                #map new props and geom and export default feature
                feature['geometry'] = new_geom
                feature['properties'] = props

                exporter.export_feature(feature)
                #be chatty
                print str(props['wof:id']) + ' is done.'