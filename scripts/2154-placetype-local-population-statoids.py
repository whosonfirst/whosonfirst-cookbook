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
          #id,country,name,placetype,geom_type,set_wof_c_hasc_id,set_statoids_props,set_placetype_local_en,repo,set_population,set_pop_value,set_pop_src,set_pop_year,set_name_en,set_label_long,set_name,wof_c_hasc_id,_st_level,_st_name_of_division,_st_country,_st_statoid,_st_secondary,_st_iso,_st_gec,_st_type,_st_population,_st_as_of_date,_st_area_km,_st_area_mi,_st_capital,_st_tz
          #"85632727",AN,Netherlands,country,Point,,"0",country,whosonfirst-data-admin-an,"1","27726",wd,"2022",,,,AN,,,,,,,,,,,,,,
          #"85632733",XS,Somaliland,country,Point,,"0",disputed territory,whosonfirst-data-admin-xs,"1","5096159",naturalearth,"2014",,,,XS,,,,,,,,,,,,,,
          #"1796661357",MA,Béni Mellal-Khénifra,region,Polygon,MA.BK,"1",region,whosonfirst-data-admin-ma,"1","2520776",statoids,2014-09-01,,Béni Mellal-Khénifra Region,,,"1",Béni Mellal-Khénifra,MA,,,"05",,region,"2520776",2014-09-01,"33,208","12,822",Béni Mellal,+0~
          #"1796661359",MA,Casablanca-Settat,region,Polygon,MA.CS,"1",region,whosonfirst-data-admin-ma,"1","6861739",statoids,2014-09-01,,Casablanca-Settat Region,,,"1",Casablanca-Settat,MA,,,"06",,region,"6861739",2014-09-01,"20,166","7,786",Casablanca,+0~

          # what types of actions will we take?
          #
          # if this is not "", then set WOF property to the value of this column
          set_placetype_local_en = row['set_placetype_local_en']
          #
          # if these related are not "", then set WOF property to the value of this column
          set_name = row['set_name']              # some had non-ASCII characters
          set_name_en = row['set_name_en']        # Some had placetypes in the names in error
          set_label_long = row['set_label_long']  # Regenerate if any name or placetype local change
          #
          # if this is not "", then set WOF property to the value of this column
          set_wof_c_hasc_id = row['set_wof_c_hasc_id']
          #
          # if value is "1" then set the WOF population properties using explicate column values
          set_population = row['set_population']
          #
          # if this is "1", then set WOF statoids properties using explicate column values
          set_statoids_props = row['set_statoids_props']

          # gather population values
          population = row['set_pop_value']
          pop_src = row['set_pop_src']
          pop_year = row['set_pop_year']

          # gather statoids properties
          #row['_st_level'] # this is a WOF-ism prepping the data for import
          name_statoids = row['_st_name_of_division']
          country = row['_st_country']
          #hasc = row['set_wof_c_hasc_id']
          statoid = row['_st_statoid']
          # always null
          #secondary = row['_st_secondary']
          iso = row['_st_iso']
          gec = row['_st_gec']
          type_statoids = row['_st_type']
          population_statoids = row['_st_population']
          date = row['_st_as_of_date']
          areakm = row['_st_area_km']
          areami = row['_st_area_mi']
          capital = row['_st_capital']
          timezone = row['_st_tz']
        except:
          ids_with_problems.append([repo,id,"CSV prop gather"])
          sys.stdout.write('\rProblem with WOF ID = {} in repo {} to gather basic props from CSV...\r'.format(id,repo))

        # Update the localized placetype labels
        try:
          # This property stores the value to set it to
          # But an empty string means take no action
          if not set_placetype_local_en == '':
            # this is one of those "single element" lists in WOF
            label = props['label:eng_x_preferred_placetype'] = [set_placetype_local_en]
        except:
          ids_with_problems.append([repo,id,"set label"])
          sys.stdout.write('\rProblem with WOF ID = {} in repo {} to set label:eng_x_preferred_placetype...\r'.format(id,repo))

        # some had non-ASCII characters
        try:
          # This property stores the value to set it to
          # But an empty string means take no action
          if not set_name == '':
            # This happens on several hundred features that weren't ASCII so OK to not store as variants
            props['wof:name'] = set_name
        except:
          ids_with_problems.append([repo,id,"set wof name"])
          sys.stdout.write('\rProblem with WOF ID = {} in repo {} to set wof:name...\r'.format(id,repo))

        # Some had placetypes in the names in error
        try:
          # This property stores the value to set it to
          # But an empty string means take no action
          if not set_name_en == '':
            # this is one of those "single element" lists in WOF
            # We might save the previous value as alt, but they were a lot of junk?
            props['name:eng_x_preferred'] = [set_name_en]
        except:
          ids_with_problems.append([repo,id,"set English name"])
          sys.stdout.write('\rProblem with WOF ID = {} in repo {} to set English name...\r'.format(id,repo))

        # Regenerate if any name or placetype local change
        try:
          # This property stores the value to set it to
          # But an empty string means take no action
          if not set_label_long == '':
            # this is one of those "single element" lists in WOF
            # This is just a WOF-ism so no need to track earlier variants
            props['label:eng_x_preferred_longname'] = [set_label_long]
        except:
          ids_with_problems.append([repo,id,"set English long label"])
          sys.stdout.write('\rProblem with WOF ID = {} in repo {} to set English long label...\r'.format(id,repo))

        # Update Statoids HASC concordances
        try:
          # This property stores the value to set it to
          # But an empty string means take no action
          if not set_wof_c_hasc_id == '':
            concordances = props.get('wof:concordances', {})
            concordances['hasc:id'] = set_wof_c_hasc_id
        except:
          ids_with_problems.append([repo,id,"set concordance"])
          sys.stdout.write("\rProblem with WOF ID = {} in repo {} to set wof:concordances['hasc:id']...\r".format(id,repo))

        # Can we harvest more Statoids properties?
        try:
          #straight statoids mappings...
          if set_statoids_props == '1':
            # though there are plenty of holes in the data...
            # so guard against setting empty string values
            if not name_statoids == '':
              props['statoids:name'] = name_statoids
            if not country == '':
              props['statoids:country'] = country
            if not set_wof_c_hasc_id == '':
              props['statoids:hasc'] = set_wof_c_hasc_id
            if not statoid == '':
              props['statoids:statoid'] = statoid
            # This is always null, so skip
            #if not secondary == '':
            #  props['statoids:secondary'] = secondary
            if not iso == '':
              props['statoids:iso'] = iso
            if not gec == '':
              props['statoids:gec'] = gec
            if not type_statoids == '':
              props['statoids:type'] = type_statoids
            if not population_statoids == '':
              # sometimes Statoids has commas in population as 1000s separator, remove them
              props['statoids:population'] = int(population_statoids.replace(',', ''))
            if not date == '':
              props['statoids:date'] = date
            if not areakm == '':
              props['statoids:areakm'] = int(float(areakm.replace(',', '')))
            if not areami == '':
              props['statoids:areami'] = int(float(areami.replace(',', '')))
            if not capital == '':
              props['statoids:capital'] = capital
            if not timezone == '':
              props['statoids:timezone'] = timezone

            #inception date
            # (nvkelso) I'm not sure why we did this before
            # since we already use this to set the population source date
            #if not date == '':
            #  props['edtf:inception'] = date
        except:
          ids_with_problems.append([repo,id,"set statoids"])
          sys.stdout.write("\r\rProblem with WOF ID = {} in repo {} to set statoids:* properties or edtf:inception...\r".format(id,repo))

        # populations
        try:
          #population, population_rank, and src:population
          if set_population == '1':
            props['wof:population'] = int(population)
            props['src:population'] = pop_src
            props['src:population_year'] = pop_year

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
        except:
          ids_with_problems.append([repo,id,"set population"])
          sys.stdout.write("\rProblem with WOF ID = {} in repo {} to set population related properties...\r".format(id,repo))

        # MZ is_current
        try:
          # if we're doing surgery, then the place must be current
          # but we do have some trash points in the file
          # so be conservative on just polygons
          if row['geom_type'] == 'Polygon':
            props['mz:is_current'] = 1
        except:
          ids_with_problems.append([repo,id,"set current"])
          sys.stdout.write("\rProblem with WOF ID = {} in repo {} to set that it's current...\r".format(id,repo))

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