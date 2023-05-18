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
      # id,name,repo,placetype,fips_bad,geoid,population,population_year,pop_src,parent_id
      # 102080397,Yauco,whosonfirst-data-admin-pr,county,,72153,"34,048",2020,uscensus,85633729


      # We want to ensure top level features have manual review
      # and they have updated populations

      # See also:
      # https://www.census.gov/programs-surveys/geography/guidance/geo-identifiers.html

      try:
        population = int(row['population'])


        # Also set the WOF property for source of population
        props['src:population'] = row['pop_src']

        # almost all data is from uscensus
        if row['pop_src'] == 'uscensus':
          props['uscensus:population'] = population
          # Also set the WOF property for population
          props['wof:population'] = population
          # set population_rank, too
          props['uscensus:population_year'] = int(row['population_year'])
        # but 1 is from wikidata (wd)
        else:
          props['wd:population'] = population
          # Also set the WOF property for population
          props['wof:population'] = population
          # set population_rank, too
          props['wd:population_year'] = int(row['population_year'])

        # Also set the WOF property for source year of population
        # (in YYYY string EDTF format), in the CSV this is already YYYY format
        props['src:population_date'] = str(row['population_year'])

      except:
        population = None

      # set population_rank, too
      # https://github.com/whosonfirst/whosonfirst-properties/blob/main/properties/wof/README.md#population_rank
      if not population < 1:
        # 1 billion
        if population >= 1000000000:
            props['wof:population_rank'] = 18
        # 100 million
        elif population >= 100000000:
            props['wof:population_rank'] = 17
        # 50 million
        elif population >= 50000000:
            props['wof:population_rank'] = 16
        # 20 million
        elif population >= 20000000:
            props['wof:population_rank'] = 15
        # 10 million
        elif population >= 10000000:
            props['wof:population_rank'] = 14
        # 5 million
        elif population >= 5000000:
            props['wof:population_rank'] = 13
        # 1 million
        elif population >= 1000000:
            props['wof:population_rank'] = 12
        # 500 thousand
        elif population >= 500000:
            props['wof:population_rank'] = 11
        # 200 thousand
        elif population >= 200000:
            props['wof:population_rank'] = 10
        # 100 thousand
        elif population >= 100000:
            props['wof:population_rank'] = 9
        # 50 thousand
        elif population >= 50000:
            props['wof:population_rank'] = 8
        elif population >= 20000:
            props['wof:population_rank'] = 7
        elif population >= 10000:
            props['wof:population_rank'] = 6
        elif population >= 5000:
            props['wof:population_rank'] = 5
        elif population >= 2000:
            props['wof:population_rank'] = 4
        elif population >= 1000:
            props['wof:population_rank'] = 3
        elif population >= 200:
            props['wof:population_rank'] = 2
        elif population > 0:
            props['wof:population_rank'] = 1
        else:
            props['wof:population_rank'] = 0

      # first make sure the WOF document has a concordances list and add it if not
      if not 'wof:concordances' in props:
        props['wof:concordances'] = {}

      # then set the concordance for this WOF feature's NUTS ID(s)
      if 'wof:concordances' in props:
        # always set the manual value, if it's present
        # (it's missing for one value)
        if row['geoid']:
          props['wof:concordances']['uscensus:geoid'] = row['geoid']

      # an odd thing happened to Puerto Rico where the dependency and region collapsed
      # but all the counties still point to the superseded region, so fix that
      if row['parent_id']:
        props['wof:parent_id'] = row['parent_id']

      # in this case, we always have something to say
      exporter.export_feature(feature)

      row_cursor += 1