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

  # which NUTS level determines which WOF NUTS properties to set with what CSV column
  if "wof_nuts_level0_concordances_population.csv" in places:
      nuts_level = "0"
  elif "wof_nuts_level1_concordances_population.csv" in places:
      nuts_level = "1"
  elif "wof_nuts_level2_concordances_population.csv" in places:
      nuts_level = "2"
  elif "wof_nuts_level3_concordances_population.csv" in places:
      nuts_level = "3"
  elif "wof_nuts_lau_concordances.csv" in places:
      nuts_level = "lau"

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

      # NUTS metadata
      # https://gisco-services.ec.europa.eu/distribution/v2/nuts/nuts-2021-metadata.pdf

      # set the name spaced NUTS properties
      if nuts_level == '0':
        # DATA SAMPLE
        # id    parent_id    name    placetype    country    repo    j_NUTS_ID    j_LEVL_COD    j_CNTR_COD    j_NAME_LAT    j_NUTS_NAM    j_MOUNT_TY    j_URBN_TYP    j_COAST_TY    demo_r_pjangrp3_year    demo_r_pjangrp3_population
        # 85633105    102191581    Czech Republic    country    CZ    whosonfirst-data-admin-cz    CZ    0    CZ    Česko    Česko    0    0    0    2022    10516707

        props['eurostat:nuts_2021_id'] = row['j_NUTS_ID']
        props['eurostat:level_code'] = str( row['j_LEVL_COD'] )
        props['eurostat:country_code'] = row['j_CNTR_COD']
        props['eurostat:name_latin'] = row['j_NAME_LAT']
        props['eurostat:name_local'] = row['j_NUTS_NAM']
        # These are present in the source but always 0 because
        # Eurostat doesn't track them until NUTS level 3 but Eurostat
        # delivers a single GeoPackage with all layers in same schema
        #props['eurostat:mount_type'] = row['j_MOUNT_TY']
        #props['eurostat:urban_type'] = row['j_URBN_TYP']
        #props['eurostat:coast_type'] = row['j_COAST_TY']
        # NUTS 0 generally matches WOF country, except EL for GR (Greece) and
        # UK for GB (United Kingdom)
        # WOF statistical placetype geometries that match Eurostats but don't have
        # EuroGeographics geometry copyright limitations
        props['eurostat:nuts_2021_level_0'] = row['j_NUTS_ID']

        # Eurostat population is open data, so we can import into WOF properties
        # Eurostats population from: demo_r_pjangrp3_page_tabular_clean.tsv
        # https://ec.europa.eu/eurostat/databrowser/view/demo_r_pjangrp3/default/table?lang=en
        population = int(row['demo_r_pjangrp3_population'])

        props['eurostat:population'] = population
        # Also set the WOF property for population
        props['wof:population'] = population
        # set population_rank, too (BELOW)

        # Also set the WOF property for source of population
        props['src:population'] = 'eurostat'
        props['eurostat:population_year'] = int(row['demo_r_pjangrp3_year'])
        # Also set the WOF property for source year of population
        # (in YYYY string EDTF format), in the CSV this is already YYYY format
        props['src:population_date'] = str(row['demo_r_pjangrp3_year'])

      elif nuts_level == '1':
        # DATA SAMPLE
        # id    parent_id    name    placetype    country    repo    j_NUTS_ID    j_LEVL_COD    j_CNTR_COD    j_NAME_LAT    j_NUTS_NAM    j_MOUNT_TY    j_URBN_TYP    j_COAST_TY    j_n0_NUTS_    demo_r_pjangrp3_year    demo_r_pjangrp3_population
        # 404227357    85632997    Flemish Region    macroregion    BE    whosonfirst-data-admin-be    BE2    1    BE    Vlaams Gewest    Vlaams Gewest    0    0    0    BE    2022    6709787

        props['eurostat:nuts_2021_id'] = row['j_NUTS_ID']
        props['eurostat:level_code'] = str( row['j_LEVL_COD'] )
        props['eurostat:country_code'] = row['j_CNTR_COD']
        props['eurostat:name_latin'] = row['j_NAME_LAT']
        props['eurostat:name_local'] = row['j_NUTS_NAM']
        # These are present in the source but always 0 because
        # Eurostat doesn't track them until NUTS level 3 but Eurostat
        # delivers a single GeoPackage with all layers in same schema
        #props['eurostat:mount_type'] = row['j_MOUNT_TY']
        #props['eurostat:urban_type'] = row['j_URBN_TYP']
        #props['eurostat:coast_type'] = row['j_COAST_TY']
        # We include these properties so we can optimistically someday create
        # WOF statistical placetype geometries that match Eurostats but don't have
        # EuroGeographics geometry copyright limitations
        props['eurostat:nuts_2021_level_0'] = row['j_n0_NUTS_']
        props['eurostat:nuts_2021_level_1'] = row['j_NUTS_ID']

        # Eurostat population is open data, so we can import into WOF properties
        # Eurostats population from: demo_r_pjangrp3_page_tabular_clean.tsv
        # https://ec.europa.eu/eurostat/databrowser/view/demo_r_pjangrp3/default/table?lang=en
        population = int(row['demo_r_pjangrp3_population'])

        props['eurostat:population'] = population
        # Also set the WOF property for population
        props['wof:population'] = population
        # set population_rank, too (BELOW)

        # Also set the WOF property for source of population
        props['src:population'] = 'eurostat'
        props['eurostat:population_year'] = int(row['demo_r_pjangrp3_year'])
        # Also set the WOF property for source year of population
        # (in YYYY string EDTF format), in the CSV this is already YYYY format
        props['src:population_date'] = str(row['demo_r_pjangrp3_year'])

      elif nuts_level == '2':
        # DATA SAMPLE
        # id    parent_id    name    placetype    country    repo    j_NUTS_ID    j_LEVL_COD    j_CNTR_COD    j_NAME_LAT    j_NUTS_NAM    j_MOUNT_TY    j_URBN_TYP    j_COAST_TY    j_n1_NUTS_    j_n0_NUTS_    demo_r_pjangrp3_year    demo_r_pjangrp3_population
        # i85681649    85632785    Vorarlberg    region    AT    whosonfirst-data-admin-at    AT34    2    AT    Vorarlberg    Vorarlberg    0    0    0    AT3    AT    2022    401674

        props['eurostat:nuts_2021_id'] = row['j_NUTS_ID']
        props['eurostat:level_code'] = str( row['j_LEVL_COD'] )
        props['eurostat:country_code'] = row['j_CNTR_COD']
        props['eurostat:name_latin'] = row['j_NAME_LAT']
        props['eurostat:name_local'] = row['j_NUTS_NAM']
        # These are present in the source but always 0 because
        # Eurostat doesn't track them until NUTS level 3 but Eurostat
        # delivers a single GeoPackage with all layers in same schema
        #props['eurostat:mount_type'] = row['j_MOUNT_TY']
        #props['eurostat:urban_type'] = row['j_URBN_TYP']
        #props['eurostat:coast_type'] = row['j_COAST_TY']
        # We include these properties so we can optimistically someday create
        # WOF statistical placetype geometries that match Eurostats but don't have
        # EuroGeographics geometry copyright limitations
        props['eurostat:nuts_2021_level_0'] = row['j_n0_NUTS_']
        props['eurostat:nuts_2021_level_1'] = row['j_n1_NUTS_']
        props['eurostat:nuts_2021_level_2'] = row['j_NUTS_ID']

        # Eurostat population is open data, so we can import into WOF properties
        # Eurostats population from: demo_r_pjangrp3_page_tabular_clean.tsv
        # https://ec.europa.eu/eurostat/databrowser/view/demo_r_pjangrp3/default/table?lang=en
        population = int(row['demo_r_pjangrp3_population'])

        props['eurostat:population'] = population
        # Also set the WOF property for population
        props['wof:population'] = population
        # set population_rank, too (BELOW)

        # Also set the WOF property for source of population
        props['src:population'] = 'eurostat'
        props['eurostat:population_year'] = int(row['demo_r_pjangrp3_year'])
        # Also set the WOF property for source year of population
        # (in YYYY string EDTF format), in the CSV this is already YYYY format
        props['src:population_date'] = str(row['demo_r_pjangrp3_year'])

      elif nuts_level == '3':
        # DATA SAMPLE
        # id    parent_id    name    placetype    country    repo    j_NUTS_ID    j_LEVL_COD    j_CNTR_COD    j_NAME_LAT    j_NUTS_NAM    j_MOUNT_TY    j_URBN_TYP    j_COAST_TY    j_n2_NUTS_    j_n1_NUTS_    j_n0_NUTS_    demo_r_pjangrp3_year    demo_r_pjangrp3_population
        # 102049907    85681727    Virton    county    BE    whosonfirst-data-admin-be    BE345    3    BE    Arr. Virton    Arr. Virton    4    3    3    BE34    BE3    BE    2022    54821

        props['eurostat:nuts_2021_id'] = row['j_NUTS_ID']
        props['eurostat:level_code'] = row['j_LEVL_COD']
        props['eurostat:country_code'] = row['j_CNTR_COD']
        props['eurostat:name_latin'] = row['j_NAME_LAT']
        props['eurostat:name_local'] = row['j_NUTS_NAM']
        # Unclear if this is "mountain" or "metro" or?
        # Doesn't match this website
        # https://ec.europa.eu/eurostat/web/nuts/tercet-territorial-typologies
        props['eurostat:mount_type'] = row['j_MOUNT_TY']
        props['eurostat:urban_type'] = row['j_URBN_TYP']
        props['eurostat:coast_type'] = row['j_COAST_TY']
        # We include these properties so we can optimistically someday create
        # WOF statistical placetype geometries that match Eurostats but don't have
        # EuroGeographics geometry copyright limitations
        props['eurostat:nuts_2021_level_0'] = row['j_n0_NUTS_']
        props['eurostat:nuts_2021_level_1'] = row['j_n1_NUTS_']
        props['eurostat:nuts_2021_level_2'] = row['j_n2_NUTS_']
        props['eurostat:nuts_2021_level_3'] = row['j_NUTS_ID']

        # Eurostat population is open data, so we can import into WOF properties
        # Eurostats population from: demo_r_pjangrp3_page_tabular_clean.tsv
        # https://ec.europa.eu/eurostat/databrowser/view/demo_r_pjangrp3/default/table?lang=en
        try:
          population = int(row['demo_r_pjangrp3_population'])

          props['eurostat:population'] = population
          # Also set the WOF property for population
          props['wof:population'] = population
          # set population_rank, too (BELOW)

          # Also set the WOF property for source of population
          props['src:population'] = 'eurostat'
          props['eurostat:population_year'] = int(row['demo_r_pjangrp3_year'])
          # Also set the WOF property for source year of population
          # (in YYYY string EDTF format), in the CSV this is already YYYY format
          props['src:population_date'] = str(row['demo_r_pjangrp3_year'])

        except:
          population = None


      elif nuts_level == 'lau':
        # DATA SAMPLE
        # id    name    placetype    country    repo    j_GISCO_ID    j_CNTR_COD    j_LAU_ID    j_LAU_NAME    j_POP_2020    j_YEAR    j_n3_NUTS_    j_n2_NUTS_    j_n1_NUTS_    j_n0_NUTS_
        # 1108959527    Koper    localadmin    SI    whosonfirst-data-admin-si    SI_050    SI    050    Koper/Capodistria    52630    2020    SI044    SI04    SI0    SI

        props['eurostat:gisco_id'] = row['j_GISCO_ID']
        props['eurostat:nuts_2021_id'] = row['j_LAU_ID']
        props['eurostat:level_code'] = 'lau'
        props['eurostat:country_code'] = row['j_CNTR_COD']
        #props['eurostat:name_latin'] = row['j_NAME_LAT']    # not available from source
        props['eurostat:name_local'] = row['j_LAU_NAME']
        # Eurostat receives annual lists of local administrative units, their
        # population, and their area (to calculate population density)
        # (this is separate from geometries from EuroGeographics and under general
        # Eurostat open data license, so we can import into WOF properties, too)

        try:
          population = int(row['j_POP_2020'])

          props['eurostat:population'] = population
          # Also set the WOF property for population
          props['wof:population'] = population
          # set population_rank, too

          # Also set the WOF property for source of population
          props['src:population'] = 'eurostat'
          props['eurostat:population_year'] = int(row['j_YEAR'])
          # Also set the WOF property for source year of population
          # (in YYYY string EDTF format), in the CSV this is already YYYY format
          props['src:population_date'] = str(row['j_YEAR'])

        except:
          population = None

        # We include these properties so we can optimistically someday create
        # WOF statistical placetype geometries that match Eurostats but don't have
        # EuroGeographics geometry copyright limitations
        # Eurostats didn't give them directly to us, they are from spatial join
        # Though Eurostats does publish lookup tables
        props['eurostat:nuts_2021_level_0'] = row['j_n0_NUTS_']
        props['eurostat:nuts_2021_level_1'] = row['j_n1_NUTS_']
        props['eurostat:nuts_2021_level_2'] = row['j_n2_NUTS_']
        props['eurostat:nuts_2021_level_3'] = row['j_n3_NUTS_']
        # Eurostats did give us this one
        props['eurostat:nuts_2021_level_lau'] = row['j_LAU_ID']

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
        if nuts_level == 'lau':
            # NUTS have different vintages (this is important), postfix with year
            props['wof:concordances']["eurostat:nuts_2021_id"] = row['j_LAU_ID']
            props['wof:concordances']["eg:gisco_id"] = row['j_GISCO_ID']
        else:
            # NUTS have different vintages (this is important), postfix with year
            props['wof:concordances']["eurostat:nuts_2021_id"] = row['j_NUTS_ID']

      exporter.export_feature(feature)

      row_cursor += 1