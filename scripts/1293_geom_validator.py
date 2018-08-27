#make geoms valid, per issue #1293
#stepps00 - 08.27.2018

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

            if feature:
                props = feature['properties']
                geom = feature['geometry']

                poly = osgeo.ogr.CreateGeometryFromJson(geojson.dumps(geom))
                valid = poly.IsValid()

                if not valid:
                    new_poly = poly.Buffer(0.0)
                    valid_new_poly = new_poly.IsValid()

                    if valid_new_poly:
                        import shapely.wkt

                        str_poly = str(new_poly)
                        shp  = shapely.wkt.loads(str_poly)
                        shp1 = shapely.geometry.mapping(shp)

                        feature['geometry'] = shp1

                        exporter.export_feature(feature)
                        print 'done with: ' + str(id)

                    else:
                        print 'ERR: ' + str(id) + ' should be valid!'

                else:
                    print 'ERR: ' + str(id) + ' should not be valid!'