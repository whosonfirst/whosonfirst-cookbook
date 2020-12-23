#stepps00 - 07-24-2018
#
#https://github.com/whosonfirst-data/whosonfirst-data/issues/1214
#
#used to supersede two ids into a single new id
#assumes you can use one of the superseded_by 
#geometries for the new record's geometry
#

import sys
import os
import logging
import optparse
import csv
import datetime
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

        #read in ids for the two deprecated features and the newly minted wof:id
        correct_geom_id = row['correct_geom_id']
        incorrect_geom_id = row['incorrect_geom_id']
        new_feature_id = row['new_feature_id']
   
        if new_feature_id:

            #create a new feature variable out of the existing record with the correct geom
            new_feature = mapzen.whosonfirst.utils.load(source, correct_geom_id)

            if new_feature:
                new_feature_props = new_feature['properties']

                #step one: update ids
                new_feature['id'] = int(new_feature_id)
                new_feature_props['wof:id'] = int(new_feature_id)

                #step two: update placetype
                new_feature_props['wof:placetype'] = 'locality'

                #step three: supersedes work
                new_feature_props['wof:supersedes'] = [int(correct_geom_id),int(incorrect_geom_id)]
                new_feature['properties'] = new_feature_props

                #write changes out
                exporter.export_feature(new_feature)

        if correct_geom_id:

            #load first superseded_by record
            correct_geom_feature = mapzen.whosonfirst.utils.load(source, correct_geom_id)

            if correct_geom_feature:
                correct_geom_feature_props = correct_geom_feature['properties']

                #update edtf, is_current, and superseded_by properties
                correct_geom_feature_props['wof:superseded_by'] = [int(new_feature_id)]
                correct_geom_feature_props['mz:is_current'] = 0
                correct_geom_feature_props['edtf:deprecated'] = datetime.datetime.today().strftime('%Y-%m-%d')
                correct_geom_feature_props['edtf:superseded'] = datetime.datetime.today().strftime('%Y-%m-%d')

                #write changes out
                exporter.export_feature(correct_geom_feature)

        #second record
        if incorrect_geom_id:

            #load second superseded_by record
            incorrect_geom_feature = mapzen.whosonfirst.utils.load(source, incorrect_geom_id)

            if incorrect_geom_feature:
                incorrect_geom_feature_props = incorrect_geom_feature['properties']

                #update edtf, is_current, and superseded_by properties
                incorrect_geom_feature_props['wof:superseded_by'] = [int(new_feature_id)]
                incorrect_geom_feature_props['mz:is_current'] = 0
                incorrect_geom_feature_props['edtf:deprecated'] = datetime.datetime.today().strftime('%Y-%m-%d')
                incorrect_geom_feature_props['edtf:superseded'] = datetime.datetime.today().strftime('%Y-%m-%d')

                #write changes out
                exporter.export_feature(incorrect_geom_feature)