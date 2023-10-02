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
  ids_with_problems = []
  ids_with_overwritten_labels = []

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

    # which record are we operating on?
    id           = row['id']
    # where can we find that record's file?
    repo         = row['repo']
    #name        = row['name']

    if id:
      output = basepath + str(repo) + "/data/"

      exporter = mapzen.whosonfirst.export.flatfile(output)

      feature = mapzen.whosonfirst.utils.load(output, id)

      # guard against bogus WOF ids not matching any feature
      if feature:
        props = feature['properties']

        try:
          #fid,id,country,name,name_en,placetype,latitude,longitude,repo,geom_type,placetype_label,label_long,concord_hasc_id,wof_coterminous,population,population_src,population_date,concordance_iso_id,concordance_us_geoid,concordance_eg_gisco_id,concordance_inegi_id,meso_local_id,uscensus_geoid,uscensus_name,uscensus_namelsad,qs_source,qs_type,qs_pop,qs_a1r,qs_a1r_lc,qs_a1_lc,qs_a2r_lc,qs_a2_lc,eurostat_population,iso_country,iso_subdivision,ne_fips,ne_gn_a1_code,ne_gns_adm1,ne_iso_3166_2,statoids_gec,statoids_hasc,statoids_country,statoids_iso,unlc_subdivision,wof_subdivision,set_concordance_key,set_concordance_val,maybe_hasc,set_concordance_key2,set_concordance_val2,set_country,set_concordance_key_tmp,set_concordance_val_tmp
          #"42707","85671213",FO,Eysturoyar,Faroe Islands,region,62.185604,-7.058429,whosonfirst-data-admin-fo,Polygon,,Eysturoyar Region,FO.OS,,,,,,,,,,,,,Natural Earth,Region,,,,FRO-1443,,,,FO,,FO00,FO.,FO00,FO-,,,,,,,iso:code_pseudo,FO,"2",,,,,
          #"42708","421203361",MH,Lib,Lib,region,8.3136,167.38,whosonfirst-data-admin-mh,Point,,,,,"147",quattroshapes,,,,,,,,,,,,,,,,,,,MH,,,,,,,,,,,,iso:code,MH-LIB,"2",,,,,
          #"42709","1108805699",BF,Centre-Sud,Centre Sud,region,11.315937,-1.083142,whosonfirst-data-admin-bf,Polygon,region,Centre-Sud Region,BF.CS,,"638379",statoids,2006-12-23,BF-07,,,,,,,,,,,,,,,,,BF,,,,,,UV85,BF.CS,BF,"07",,,iso:code,BF-07,,,,,,
          #"42710","1108805941",GE,Shida Kartli,Shida Kartli,region,42.076385,43.951089,whosonfirst-data-admin-ge,Polygon,region,Shida Kartli Region,GE.SD,,"314039",statoids,2002-01-17,GE-SK,,,,,,,,,,,,,,,,,GE,,,,,,GG73,GE.SD,GE,SK,,,iso:code,GE-SK,,,,,,
          #"46823","85688675",US,Alabama,Alabama,region,32.688053,-86.810585,whosonfirst-data-admin-us,Polygon,state,Alabama,US.AL,,"5024279",uscensus,"2020",US-AL,"01",,,,,,,US Census,G4000,,,,"01",,,,US,US-AL,US01,US.AL,,US-AL,US01,US.AL,US,AL,US-AL,US-AL,uscensus:geoid,"01",,iso:code,US-AL,,iso:code,US-AL
          #"46827","85688637",US,California,California,region,36.531544,-119.586168,whosonfirst-data-admin-us,Polygon,state,California,US.CA,,"39538223",uscensus,"2020",US-CA,"06",,,,,,,US Census,G4000,,,,"06",,,,US,US-CA,US06,US.CA,,US-CA,US06,US.CA,US,CA,US-CA,US-CA,uscensus:geoid,"06",,iso:code,US-CA,,iso:code,US-CA

          # what types of actions will we take?
          #
          set_concordance_key = row['set_concordance_key']
          set_concordance_val = row['set_concordance_val']
          set_concordance_key2 = row['set_concordance_key2']
          set_concordance_val2 = row['set_concordance_val2']
          #
          # This is just for a handful of records (points from bad outdated import)
          set_country = row['set_country']
        except:
          ids_with_problems.append([repo,id,"CSV prop gather"])
          sys.stdout.write('\rProblem with WOF ID = {} in repo {} to gather basic props from CSV...\r'.format(id,repo))

        # Update basic concordance 1
        try:
          # This property stores the value to set it to
          # But an empty string means take no action
          if not set_concordance_key == '' and not set_concordance_val == '':
            if 'wof:concordances' in props:
              concordances = props.get('wof:concordances', {})
              concordances[set_concordance_key] = set_concordance_val
            else:
              props['wof:concordances'] = {set_concordance_key: set_concordance_val}
            # also set this key as the official concordance key
            props['wof:concordances_official'] = set_concordance_key

            if not set_concordance_key == 'iso:code_historic':
              props['mz:is_current'] = 1
        except:
          ids_with_problems.append([repo,id,"set concordance 1"])
          sys.stdout.write("\rProblem with WOF ID = {} in repo {} to set wof:concordances['{}']...\r".format(id,repo,'set_concordance_key'))

        # Update basic concordance 2
        try:
          # This property stores the value to set it to
          # But an empty string means take no action
          if not set_concordance_key2 == '' and not set_concordance_val2 == '':
            if 'wof:concordances' in props:
              concordances = props.get('wof:concordances', {})
              concordances[set_concordance_key2] = set_concordance_val2
            else:
              props['wof:concordances'] = {set_concordance_key2: set_concordance_val2}
            # also add this key to the list of alternate official concordance keys
            props['wof:concordances_official_alt'] = [set_concordance_key2]

            if not set_concordance_key == 'iso:code_historic':
              props['mz:is_current'] = 1

        except:
          ids_with_problems.append([repo,id,"set concordance 2"])
          sys.stdout.write("\rProblem with WOF ID = {} in repo {} to set wof:concordances['{}']...\r".format(id,repo,'set_concordance_key2'))

        # country (rare)
        try:
          if not set_country == '':
            props['wof:country'] = set_country
        except:
          ids_with_problems.append([repo,id,"country"])
          sys.stdout.write("\rProblem with WOF ID = {} in repo {} to set it's country...\r".format(id,repo))

        # store the props back on the records
        feature['properties'] = props

        exporter.export_feature(feature)

        row_cursor += 1
    else:
      sys.stdout.write('\r row {} missing WOF ID'.format(row))

  if len(ids_with_problems) > 0:
    print("There were some problems:")
    for problem in ids_with_problems:
      print(problem)

  if len(ids_with_overwritten_labels) > 0:
    print("There were some existing labels:")
    for label in ids_with_overwritten_labels:
      print(label)