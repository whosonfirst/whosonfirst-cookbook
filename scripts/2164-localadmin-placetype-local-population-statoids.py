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
          #fid,id,country,name,name_en,placetype,repo,geom_type,placetype_label,label_long,concord_hasc_id,wof_coterminous,population,population_src,population_date,concordance_us_geoid,concordance_eg_gisco_id,uscensus_geoid,uscensus_name,uscensus_namelsad,qs_source,qs_type,qs_pop,qs_a1r,qs_a1r_lc,qs_a1_lc,qs_la_lc,eurostat_population,set_concordance_key,set_concordance_value,set_label_placetype_en,set_label_placetype_lang1,set_label_placetype_lang1_3char,set_label_placetype_lang2,set_label_placetype_lang2_3char,set_label_placetype_lang3,set_label_placetype_lang3_3char,set_concordance_key2,set_concordance_value2,funky,deprecate
          #"1","1108835949",AT,Helfenberg,,localadmin,whosonfirst-data-admin-at,Polygon,,,,,"989",geonames,,,,,,,,,,,,,,,austriaod:number,"41310",municipality,gemeinde,deu,,,,,,,"0",
          #"2","1108839397",AT,Großlobming,,localadmin,whosonfirst-data-admin-at,Polygon,,,,,,,,,,,,,,,,,,,,,austriaod:number,"62039",municipality,gemeinde,deu,,,,,,,"0",
          #"3","1108837537",AT,Lans,,localadmin,whosonfirst-data-admin-at,Polygon,,,,,"1083",geonames,,,,,,,,,,,,,,,austriaod:number,"70325",municipality,gemeinde,deu,,,,,,,"0",
          #"4","1108838661",AT,Pöttsching,,localadmin,whosonfirst-data-admin-at,Polygon,,,,,,,,,,,,,,,,,,,,,austriaod:number,"10609",municipality,gemeinde,deu,,,,,,,"0",
          #"5","1108835171",AT,Bruck-Waasen,,localadmin,whosonfirst-data-admin-at,Polygon,,,,,"2336",geonames,,,,,,,,,,,,,,,austriaod:number,"40803",municipality,gemeinde,deu,,,,,,,"0",
          #"6","1108835207",AT,Peuerbach,,localadmin,whosonfirst-data-admin-at,Polygon,,,,,,,,,,,,,,,,,,,,,austriaod:number,"40819",municipality,gemeinde,deu,,,,,,,"0",

          # what types of actions will we take?
          #
          # if this is not "", then set WOF property to the value of this column
          set_placetype_local_en = row['set_label_placetype_en']
          #
          set_label_placetype_lang1       = row['set_label_placetype_lang1']
          set_label_placetype_lang1_3char = row['set_label_placetype_lang1_3char']
          set_label_placetype_lang2       = row['set_label_placetype_lang2']
          set_label_placetype_lang2_3char = row['set_label_placetype_lang2_3char']
          set_label_placetype_lang3       = row['set_label_placetype_lang3']
          set_label_placetype_lang3_3char = row['set_label_placetype_lang3_3char']
          #
          set_concordance_key = row['set_concordance_key']
          set_concordance_val = row['set_concordance_value']
          set_concordance_key2 = row['set_concordance_key2']
          set_concordance_val2 = row['set_concordance_value2']
          #
          # This is just for a handful of records (points from bad outdated import)
          deprecate = row['deprecate']
        except:
          ids_with_problems.append([repo,id,"CSV prop gather"])
          sys.stdout.write('\rProblem with WOF ID = {} in repo {} to gather basic props from CSV...\r'.format(id,repo))

        # Update the localized placetype labels ENG
        try:
          # This property stores the value to set it to
          # But an empty string means take no action
          if not set_placetype_local_en == '':
            # this is one of those "single element" lists in WOF
            props['label:eng_x_preferred_placetype'] = [set_placetype_local_en]

            # because of earlier mistake
            if 'label:eng_x_variant_placetype' in props:
              del props['label:eng_x_variant_placetype']

            # also store the earlier version as a variant (mostly for Sudan)
            # technically a multi-element list in WOF, but first usage so shortcut
            #if not placetype_label_original_en == '':
            #  props['label:eng_x_variant_placetype'] = [placetype_label_original_en]

            if 'label:eng_x_variant_placetype' in props:
              if 'label:eng_x_preferred_placetype' in props:
                if props['label:eng_x_preferred_placetype'] == props['label:eng_x_variant_placetype']:
                  del props['label:eng_x_variant_placetype']
        except:
          ids_with_problems.append([repo,id,"set label"])
          sys.stdout.write('\rProblem with WOF ID = {} in repo {} to set label:eng_x_preferred_placetype...\r'.format(id,repo))

        # Update the localized placetype labels LANG 1
        try:
          # This property stores the value to set it to
          # But an empty string means take no action
          if not set_label_placetype_lang1 == '' and not set_label_placetype_lang1_3char == '':
            # store the earlier version as a variant (it'll be dedup'd later)
            # technically a multi-element list in WOF, but first usage so shortcut
            if 'label:' + set_label_placetype_lang1_3char + '_x_preferred_placetype' in props:
              props['label:' + set_label_placetype_lang1_3char + '_x_variant_placetype'] = props['label:' + set_label_placetype_lang1_3char + '_x_preferred_placetype']

            # set preferred value
            # this is one of those "single element" lists in WOF
            props['label:' + set_label_placetype_lang1_3char + '_x_preferred_placetype'] = [set_label_placetype_lang1]

            # dedup
            if 'label:' + set_label_placetype_lang1_3char + '_x_variant_placetype' in props:
              if 'label:' + set_label_placetype_lang1_3char + '_x_preferred_placetype' in props:
                if props['label:' + set_label_placetype_lang1_3char + '_x_preferred_placetype'] == props['label:' + set_label_placetype_lang1_3char + '_x_variant_placetype']:
                  del props['label:' + set_label_placetype_lang1_3char + '_x_variant_placetype']
        except:
          ids_with_problems.append([repo,id,"set label"])
          sys.stdout.write('\rProblem with WOF ID = {} in repo {} to set label:{}_x_preferred_placetype...\r'.format(id,repo,'lang1_3char'))

        # Update the localized placetype labels LANG 2
        try:
          # This property stores the value to set it to
          # But an empty string means take no action
          if not set_label_placetype_lang2 == '' and not set_label_placetype_lang2_3char == '':
            # store the earlier version as a variant (it'll be dedup'd later)
            # technically a multi-element list in WOF, but first usage so shortcut
            if 'label:' + set_label_placetype_lang2_3char + '_x_preferred_placetype' in props:
              props['label:' + set_label_placetype_lang2_3char + '_x_variant_placetype'] = props['label:' + set_label_placetype_lang2_3char + '_x_preferred_placetype']

            # set preferred value
            # this is one of those "single element" lists in WOF
            props['label:' + set_label_placetype_lang2_3char + '_x_preferred_placetype'] = [set_label_placetype_lang2]

            # dedup
            if 'label:' + set_label_placetype_lang2_3char + '_x_variant_placetype' in props:
              if 'label:' + set_label_placetype_lang2_3char + '_x_preferred_placetype' in props:
                if props['label:' + set_label_placetype_lang2_3char + '_x_preferred_placetype'] == props['label:' + set_label_placetype_lang2_3char + '_x_variant_placetype']:
                  del props['label:' + set_label_placetype_lang2_3char + '_x_variant_placetype']
        except:
          ids_with_problems.append([repo,id,"set label"])
          sys.stdout.write('\rProblem with WOF ID = {} in repo {} to set label:{}_x_preferred_placetype...\r'.format(id,repo,'lang2_3char'))

        # Update the localized placetype labels LANG 3
        try:
          # This property stores the value to set it to
          # But an empty string means take no action
          if not set_label_placetype_lang3 == '' and not set_label_placetype_lang3_3char == '':
            # store the earlier version as a variant (it'll be dedup'd later)
            # technically a multi-element list in WOF, but first usage so shortcut
            if 'label:' + set_label_placetype_lang3_3char + '_x_preferred_placetype' in props:
              props['label:' + set_label_placetype_lang3_3char + '_x_variant_placetype'] = props['label:' + set_label_placetype_lang3_3char + '_x_preferred_placetype']

            # set preferred value
            # this is one of those "single element" lists in WOF
            props['label:' + set_label_placetype_lang3_3char + '_x_preferred_placetype'] = [set_label_placetype_lang3]

            # dedup
            if 'label:' + set_label_placetype_lang3_3char + '_x_variant_placetype' in props:
              if 'label:' + set_label_placetype_lang3_3char + '_x_preferred_placetype' in props:
                if props['label:' + set_label_placetype_lang3_3char + '_x_preferred_placetype'] == props['label:' + set_label_placetype_lang3_3char + '_x_variant_placetype']:
                  del props['label:' + set_label_placetype_lang3_3char + '_x_variant_placetype']
        except:
          ids_with_problems.append([repo,id,"set label"])
          sys.stdout.write('\rProblem with WOF ID = {} in repo {} to set label:{}_x_preferred_placetype...\r'.format(id,repo,'lang3_3char'))

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
        except:
          ids_with_problems.append([repo,id,"set concordance 2"])
          sys.stdout.write("\rProblem with WOF ID = {} in repo {} to set wof:concordances['{}']...\r".format(id,repo,'set_concordance_key2'))

        # deprecate
        try:
          # if we're doing surgery, then the place must be current
          # but we do have some trash points in the file
          # so be conservative on just polygons
          if deprecate == '1':
            props['mz:is_current'] = 0
            props['edtf:deprecated'] = '2023-09-27'
        except:
          ids_with_problems.append([repo,id,"deprecate"])
          sys.stdout.write("\rProblem with WOF ID = {} in repo {} to set that it's deprecated...\r".format(id,repo))

        # we consider these current, or near enough to current
        props['mz:is_current'] = 1

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