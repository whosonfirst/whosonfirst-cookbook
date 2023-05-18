# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

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


if __name__ == "__main__":

  opt_parser = optparse.OptionParser()
  opt_parser.add_option('-i', '--input', dest='input', action='store', default=None, help='Where to read CSV import file from')
  opt_parser.add_option('-b', '--basepath', dest='basepath', action='store', default='path/to/whosonfirst-data/', help='Directory of WOF repo checkouts')
  options, args = opt_parser.parse_args()

  places = options.input
  basepath = options.basepath

  # open the CSV file in read binary mode (file handler)
  fh = open(places, 'rb')

  # how many rows will we need to process
  # so we can indicate progress (especially for larger files)
  countrdr = csv.DictReader(fh)
  rows_total = 0
  row_cursor = 1

  for row in countrdr:
    rows_total += 1

  # don't open the file again, instead seek back to first row
  # You may not have to do this, I didn't check to see if DictReader did
  fh.seek(0)

  reader = csv.DictReader(fh)

  for row in reader:

    sys.stdout.write('\r')
    # note: 50 is a magic number for the progress bar width
    # note: 50.0 and 100.0 for float results instead of ints (which otherwise rounds to 0)
    sys.stdout.write("[{:{}}] {:.1f}% ({} of {})".format("="*int((50.0/(rows_total)*row_cursor)), 50, (100.0/(rows_total)*row_cursor), row_cursor, rows_total))
    sys.stdout.flush()

    repo         = row['repo']
    #name        = row['name']
    id           = row['id']

    if id:
      output = basepath + str(repo) + "/data/"

      exporter = mapzen.whosonfirst.export.flatfile(output)

      feature = mapzen.whosonfirst.utils.load(output, id)

      props = feature['properties']

      # DATA SAMPLE
      # id    name    placetype    repo    country    FIPS (missing leading 0s!)
      # 101732665,West Salem,locality,whosonfirst-data-admin-us,US,5586275

      # The CSV from the SQLite file has an encoding problem where strings are
      # turned into ints and we loose leading 0s (oops)
      # https://github.com/whosonfirst-data/whosonfirst-data/issues/2134
      # So we use the CSV to list which features to edit, but use the feature's
      # GeoJSON values which are correct to set the new concordances

      # See also:
      # https://www.census.gov/programs-surveys/geography/guidance/geo-identifiers.html

      # first make sure the WOF document has a concordances list and add it if not
      if not 'wof:concordances' in props:
        props['wof:concordances'] = {}

      # then set the concordance for this WOF feature's NUTS ID(s)
      if 'wof:concordances' in props:
        # only backfill uscensus:geoid values (prefer existing values)
        try:
          if props['wof:concordances']['uscensus:geoid']:
            continue
        except:
            # is there a FIPS code to backfill it with?
            if props['wof:concordances']['fips:code']:
              props['wof:concordances']['uscensus:geoid'] = props['wof:concordances']['fips:code']

              # we only want to export if we had something to say
              exporter.export_feature(feature)

      row_cursor += 1