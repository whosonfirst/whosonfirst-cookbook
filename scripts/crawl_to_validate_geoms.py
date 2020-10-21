#stepps00 2020-10-20
#updated geom validation tool using Shapely

import sys
import os
import logging
import optparse
import pprint
import datetime
import mapzen.whosonfirst.utils
import mapzen.whosonfirst.placetypes
import mapzen.whosonfirst.export
import json
import geojson
from shapely.geometry import shape, mapping
import shapely.wkt

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':

    source = os.path.abspath("/path/to/data/")
    crawl = mapzen.whosonfirst.utils.crawl(source, inflate=True)
    exporter = mapzen.whosonfirst.export.flatfile(source)

    #crawl all features, map geom and props
    for feature in crawl:

        geom = feature['geometry']
        props = feature['properties']

        #check if existing geom is valid
        geom_dump = geojson.dumps(geom)
        polygon = shape(geom)
        valid = polygon.is_valid

        #if not, use shapely to add fake buffer, test validity again
        if not valid:
            new_polygon = polygon.buffer(0.0)
            valid_new_polygon = new_polygon.is_valid

            if valid_new_polygon:
                #if valid, convert 'buffered' polygon to string, wkt, and back to json
                str_polygon = str(new_polygon)

                wtk_polygon = shapely.wkt.loads(str_polygon)
                valid_geom = shapely.geometry.mapping(wtk_polygon)

                #update feature w valid geometry
                feature['geometry'] = valid_geom

                #try to export and print id
                try:
                    exporter.export_feature(feature)
                    print 'Done with: ' + str(props['wof:id'])

                #sometimes the resulting geometry is null, so let's catch those...
                #a fix is to update the buffer to something like 0.00001
                except:
                    print 'Invalid geometry, but validation results in null geometry: ' + str(props['wof:id'])

            #guard against still invalid geometries after buffer
            if not valid_new_polygon:
                print 'Error: ' + str(props['wof:id'])
