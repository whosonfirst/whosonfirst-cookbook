#stepps00 - 2023-09-09

import sys
import os
import logging
import optparse
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
    opt_parser.add_option('-o', '--output', dest='output', action='store', default="/path/to/whosonfirst-data-admin-*/data/", help='Where to write WOF records to')
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

        #read in id and centroids explicitly
        id            = new_props['id']
        #latitude/longitude values of each geometry's inner centroid
        #can be calculated using Mapshaper
        #see: https://github.com/mbloch/mapshaper
        latitude      = float(new_props['lat'])
        longitude     = float(new_props['lng'])

        #if a valid wof:id is provided...
        if not id in ["", None]:

            feature = mapzen.whosonfirst.utils.load(output, id)

            if feature:
                #load the feature, pull out props and geom
                props = feature['properties']
                geom =  feature['geometry']

                #create a new alt file
                alt_geom = {'type': 'Feature'}

                alt_geom['properties'] = {
                    'wof:id': props.get('wof:id'),
                    'src:geom': props.get('src:geom'),
                    'src:alt_label':props.get('src:geom'), 
                    #make sure to update this property with the proper repo
                    'wof:repo':'whosonfirst-data-admin-*',
                    'wof:geomhash':props.get('wof:geomhash')
                }

                #and use old geom variable as new alt geom, export
                alt_geom['geometry'] = geom

                #set src if unknown
                if not 'src:geom' in props:
                    props['src:geom'] = 'unknown'

                #update existing feature geometry
                feature['geometry'] = new_geom

                #update src and wof props
                if 'src:geom_alt' in props:
                    props['src:geom_alt'].append(props['src:geom'])

                if 'src:geom_alt' in props:
                    props['src:geom_alt'] = [props['src:geom']]

                if 'wof:geom_alt' in props:
                    props['wof:geom_alt'].append(props['src:geom'])

                if 'wof:geom_alt' in props:
                    props['wof:geom_alt'] = [props['src:geom']]

                #set source of new geometry
                props['src:geom'] = ''

                #set centroids
                props['lbl:longitude'] = longitude 
                props['lbl:latitude'] = latitude
                #may need to update these values if mapshaper is not being used
                props['mps:longitude'] = longitude
                props['mps:latitude'] = latitude

                #export alt
                exporter.export_alt_feature(alt_geom, source=alt_geom['properties']['src:geom'])

                #export feature        
                exporter.export_feature(feature)

                print str(props['wof:id']) + ' is done.'

        #if a vallid wof:id is not provided...
        if id in ["", None]:

                #we're not loading in a new feature, we're creating one from scratch this time...
                feature = {
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
                props['mz:hierarchy_label'] = 1

                #set parent
                props['wof:parent_id'] = -1

                #iso and wof country codes
                props['wof:country'] = ''
                props['iso:country'] = ''

                #placetype
                props['wof:placetype'] = ''

                #geom/src props
                props['src:geom'] = 'whosonfirst'
                props['wof:geom'] = 'whosonfirst'
                #may need to update these values if mapshaper is not being used
                props['src:lbl_centroid'] = 'mapshaper'

                #lbl and mps lat/longs
                props['lbl:latitude'] = latitude
                props['lbl:longitude'] = longitude
                #may need to update these values if mapshaper is not being used
                props['mps:latitude'] = latitude
                props['mps:longitude'] = longitude
        
                #map new props and geom and export default feature
                feature['properties'] = props
                feature['geometry'] = new_geom
        
                exporter.export_feature(feature)

                print str(props['wof:id']) + ' is done.'