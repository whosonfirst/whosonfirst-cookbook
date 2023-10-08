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

# nvkelso - 2023-10-03
# based on script from stepps, thanks!

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":

  opt_parser = optparse.OptionParser()
  opt_parser.add_option('-i', '--input', dest='input', action='store', default=None, help='Where to read GeoJSON import file from')
  opt_parser.add_option('-b', '--basepath', dest='basepath', action='store', default='path/to/whosonfirst-data/', help='Directory of WOF repo checkouts, note trailing slash')
  opt_parser.add_option('-p', '--placetype', dest='placetype', action='store', default='region', help='Which placetype (property setting)')
  options, args = opt_parser.parse_args()

  places = options.input
  basepath = os.path.abspath(options.basepath)
  placetype = options.placetype
  print placetype

  # open the input file in read binary mode (file handler)
  fh = open(places, 'r')  # or 'rb'

  # read in the entire geojson collection
  collection = geojson.load(fh)

  # how many rows will we need to process
  # so we can indicate progress (especially for larger files)
  feature_total = len(collection['features'])
  feature_cursor = 1

  # iterate over each feature uniquely
  for row in collection['features']:
    sys.stdout.write('\r')
    # note: 50 is a magic number for the progress bar width
    # note: 50.0 and 100.0 for float results instead of ints (which otherwise rounds to 0)
    sys.stdout.write("[{:{}}] {:.1f}% ({} of {})".format("="*int((50.0/(feature_total)*feature_cursor)), 50, (100.0/(feature_total)*feature_cursor), feature_cursor, feature_total))
    sys.stdout.flush()

    # { "type": "Feature", "properties": { "fid": 8144.0, "INSPIREID": "ES.IGN.BDDAE.34132853058", "NAMEUNIT": "El Redegüelo", "CODNUT1": "ES3", "CODNUT2": "ES30", "CODNUT3": "ES300", "NUMPOINTS": 1.0, "pop_COD_IN": null, "pop_ID_REL": null, "pop_COD_PR": null, "pop_PROVIN": null, "pop_NOMBRE": null, "pop_POBLAC": null, "pop_COD__1": null, "pop_CAPITA": null, "pop_POBL_1": null, "pop_long": null, "pop_lat": null, "good": null, "id": 404338737, "wof_name": "El Redegüelo", "wof_repo": "whosonfirst-data-admin-es", "wof_popula": null, "wof_popu_1": null, "wof_popu_2": null, "wof_eurost": null, "wof_set_co": "esp-ine:code", "wof_set__1": "28023;28082", "status": 2, "note": null, "inception": null, "action": "update", "wof_id_new": null, "repo": "whosonfirst-data-admin-es", "src_geom": "esp-cnig", "country": "ES", "mps_NAMEUNIT": "El Redegüelo", "mps_long": -3.917526, "mps_lat": 40.682149 }, "geometry": { "type": "MultiPolygon", "coordinates": [ [ [ [ -3.924336819, 40.677498326 ], [ -3.924504528, 40.678461075 ], [ -3.924657767, 40.67987509 ], [ -3.924086695, 40.680251709 ], [ -3.922785484, 40.681055754 ], [ -3.920302581, 40.683015082 ], [ -3.917788262, 40.68493767 ], [ -3.913043985, 40.687537259 ], [ -3.912872858, 40.687311596 ], [ -3.908892171, 40.684464736 ], [ -3.909206692, 40.684271282 ], [ -3.913154766, 40.682471792 ], [ -3.915170506, 40.681036109 ], [ -3.917586137, 40.679170213 ], [ -3.919176218, 40.677427042 ], [ -3.920448536, 40.676933161 ], [ -3.924336819, 40.677498326 ] ] ] ] } },

    id           = row['properties']['id']
    repo         = row['properties']['repo']
    action       = row['properties']['action']
    src_geom     = row['properties']['src_geom']

    # for new and updated records, also set lbl and rev:geo points
    mps_long     = row['properties']['mps_long']
    mps_lat      = row['properties']['mps_lat']

    # when setting new records up
    country      = row['properties']['country']
    inception    = row['properties']['inception']  # edtf format

    # for all the placetypes,set esp-cnig prefixed properties
    inspireid    = row['properties']['INSPIREID']   # a concordance
    nameunit     = row['properties']['NAMEUNIT']
    connut1      = row['properties']['CODNUT1']
    connut2      = row['properties']['CODNUT2']

    if placetype == 'localadmin':
      # for just the municipality
      connut3      = row['properties']['CODNUT3']

      # for just the municipality, set esp-ine prefixed properties
      pop_code_ine          = row['properties']['pop_COD_IN']   # a concordance
      pop_id_rel            = row['properties']['pop_ID_REL']
      pop_code_prov         = row['properties']['pop_COD_PR']
      pop_provincia         = row['properties']['pop_PROVIN']
      pop_nombre_actual     = row['properties']['pop_NOMBRE']
      pop_poblacion_muni    = row['properties']['pop_POBLAC']    # 2021 census population
      pop_code_ine_capital  = row['properties']['pop_COD__1']
      pop_capital           = row['properties']['pop_CAPITA']
      pop_poblacion_capital = row['properties']['pop_POBL_1']
      pop_longitude_etrs89  = row['properties']['pop_long']
      pop_latitude_etrs89   = row['properties']['pop_lat']

    # latitude/longitude values of each geometry's inner centroid
    # can be calculated using Mapshaper
    # see: https://github.com/mbloch/mapshaper
    latitude      = float(mps_lat)
    longitude     = float(mps_long)

    if id:
      new_geom = row['geometry']

      output = basepath + "/" + repo + "/data/"
      exporter = mapzen.whosonfirst.export.flatfile(output)

      if not action == 'new':
        feature = mapzen.whosonfirst.utils.load(output, id)

        # guard against bogus WOF ids not matching any feature
        if feature:

          # if a valid wof:id is provided...
          if not id in ["", None]:
            feature = mapzen.whosonfirst.utils.load(output, id)

            if feature:
              # load the feature, pull out props and geom
              props = feature['properties']
              geom =  feature['geometry']

              # set src if unknown
              if not 'src:geom' in props:
                props['src:geom'] = 'unknown'

              # create a new alt file
              alt_geom_feature = {'type': 'Feature'}

              alt_geom_feature['properties'] = {
                  'wof:id': props.get('wof:id'),
                  'src:geom': props['src:geom'],
                  'src:alt_label': props['src:geom'],
                  # make sure to update this property with the proper repo
                  'wof:repo': repo,
                  'wof:geomhash': props.get('wof:geomhash')
              }

              # and use old geom variable as new alt geom, export
              alt_geom_feature['geometry'] = geom

              # export alt
              # WARNING: order is important here... as we change the value of
              # props['src:geom'] later but because Python vars (especially in objects)
              # are interned (pointers) and we later change the pointer's value
              exporter.export_alt_feature(alt_geom_feature, source=alt_geom_feature['properties']['src:geom'])

              # update existing feature's geometry
              feature['geometry'] = new_geom

              # update src and wof props
              # (assumes a "simple" alt geom versus a "source-usage" alt geom)
              if 'src:geom_alt' in props:
                props['src:geom_alt'].append(props['src:geom'])
              else:
                props['src:geom_alt'] = [props['src:geom']]

              # this is needed because we always want to list out the explicate,
              # fully qualified "source-usage" alt geom names... while src:geom_alt only
              # lists the source prefixes
              if 'wof:geom_alt' in props:
                props['wof:geom_alt'].append(props['src:geom'])
              else:
                props['wof:geom_alt'] = [props['src:geom']]

              # set source of new geometry
              props['src:geom'] = src_geom

              # set centroids
              props['lbl:longitude'] = longitude
              props['lbl:latitude'] = latitude
              # may need to update these values if mapshaper is not being used
              props['mps:longitude'] = longitude
              props['mps:latitude'] = latitude

              # for all the placetypes,set esp-cnig prefixed properties
              # this is also a concordance value
              if inspireid and not inspireid == '':
                props['esp-cnig:inspireid'] = inspireid
                if 'wof:concordances' in props:
                  concordances = props.get('wof:concordances', {})
                  concordances['esp-cnig:inspireid'] = inspireid
                else:
                  props['wof:concordances'] = {'esp-cnig:inspireid': inspireid}
              if nameunit and not nameunit == '':
                props['esp-cnig:nameunit'] = nameunit
              if connut1 and not connut1 == '':
                props['esp-cnig:connut1'] = connut1
              if connut2 and not connut2 == '':
                props['esp-cnig:connut2'] = connut1

              if placetype == 'localadmin':
                # continue esp-cnig properties
                if connut3 and not connut3 == '':
                  props['esp-cnig:connut3'] = connut3

                # now esp-ine properties
                # this is also a concordance value
                # it's problematic, in that it has extra spacer 0 at the end
                if pop_code_ine and not pop_code_ine == '':
                  props['esp-ine:code_ine'] = pop_code_ine
                  if 'wof:concordances' in props:
                    concordances = props.get('wof:concordances', {})
                    concordances['esp-ine:code_ine'] = pop_code_ine
                  else:
                    props['wof:concordances'] = {'esp-ine:code_ine': pop_code_ine}
                if pop_id_rel and not pop_id_rel == '':
                  props['esp-ine:id_rel'] = pop_id_rel
                if pop_code_prov and not pop_code_prov == '':
                  props['esp-ine:code_prov'] = pop_code_prov
                if pop_provincia and not pop_provincia == '':
                  props['esp-ine:provincia'] = pop_provincia
                if pop_nombre_actual and not pop_nombre_actual == '':
                  props['esp-ine:nombre_actual'] = pop_nombre_actual
                # 2021 census population
                if pop_nombre_actual and not pop_nombre_actual == '':
                  props['esp-ine:poblacion_muni'] = int(pop_poblacion_muni)
                if pop_code_ine_capital and not pop_code_ine_capital == '':
                  props['esp-ine:code_ine_capital'] = pop_code_ine_capital
                if pop_capital and not pop_capital == '':
                  props['esp-ine:capital'] = pop_capital
                if pop_poblacion_capital and not pop_poblacion_capital == '':
                  props['esp-ine:poblacion_capital'] = int(pop_poblacion_capital)
                # this is where other mapping platforms put the label, while we prefer
                # mapshaper for ours, let's carry this along...
                if pop_longitude_etrs89 and not pop_longitude_etrs89 == '':
                  props['esp-ine:longitude_etrs89'] = float(pop_longitude_etrs89)
                if pop_latitude_etrs89 and not pop_latitude_etrs89 == '':
                  props['esp-ine:longitude_etrs89'] = float(pop_latitude_etrs89)

              # export feature
              exporter.export_feature(feature)

              # print str(props['wof:id']) + ' is done.'
              feature_cursor += 1

      # we assume a new WOF feature needs to be created, with a manifest provided new ID
      else:
          # we're not loading in a new feature, we're creating one from scratch this time...
          new_feature = {
              "type":        "Feature",
              "properties":  {},
              "bbox":        {},
              "geometry":    {}
          }

          # create variables for existing props and geom to store later (geom moves to alt)
          props = new_feature['properties']
          geom = new_feature['geometry']

          props['wof:id'] = id

          # placetype
          props['wof:placetype'] = placetype

          # iso and wof country codes
          if not country == '':
            props['wof:country'] = country
            props['iso:country'] = country

          if not inception == '':
            props['edtf:inception'] = inception

          # we verified these are all current, so flag
          props['mz:is_current'] = 1
          props['mz:hierarchy_label'] = 1

          # set parent
          props['wof:parent_id'] = -1

          # geom/src props
          props['src:geom'] = src_geom
          props['wof:geom'] = src_geom
          # may need to update these values if mapshaper is not being used
          props['src:lbl_centroid'] = 'mapshaper'

          # lbl and mps lat/longs
          props['lbl:latitude'] = latitude
          props['lbl:longitude'] = longitude
          # may need to update these values if mapshaper is not being used
          props['mps:latitude'] = latitude
          props['mps:longitude'] = longitude

          # for all the placetypes,set esp-cnig prefixed properties
          # this is also a concordance value
          if inspireid and not inspireid == '':
            props['esp-cnig:inspireid'] = inspireid
            if 'wof:concordances' in props:
              concordances = props.get('wof:concordances', {})
              concordances['esp-cnig:inspireid'] = inspireid
            else:
              props['wof:concordances'] = {'esp-cnig:inspireid': inspireid}
            props['wof:concordances_official'] = 'esp-cnig:inspireid'
          if nameunit and not nameunit == '':
            props['esp-cnig:nameunit'] = nameunit
          if connut1 and not connut1 == '':
            props['esp-cnig:connut1'] = connut1
          if connut2 and not connut2 == '':
            props['esp-cnig:connut2'] = connut1

          if placetype == 'localadmin':
            # continue esp-cnig properties
            if connut3 and not connut3 == '':
              props['esp-cnig:connut3'] = connut3

            # now esp-ine properties
            # this is also a concordance value
            # it's problematic, in that it has extra spacer 0 at the end
            if pop_code_ine and not pop_code_ine == '':
              props['esp-ine:code_ine'] = pop_code_ine
              if 'wof:concordances' in props:
                concordances = props.get('wof:concordances', {})
                concordances['esp-ine:code_ine'] = pop_code_ine
              else:
                props['wof:concordances'] = {'esp-ine:code_ine': pop_code_ine}
              props['wof:concordances_official'] = 'esp-ine:code_ine'
            if pop_id_rel and not pop_id_rel == '':
              props['esp-ine:id_rel'] = pop_id_rel
            if pop_code_prov and not pop_code_prov == '':
              props['esp-ine:code_prov'] = pop_code_prov
            if pop_provincia and not pop_provincia == '':
              props['esp-ine:provincia'] = pop_provincia
            if pop_nombre_actual and not pop_nombre_actual == '':
              props['esp-ine:nombre_actual'] = pop_nombre_actual
            # 2021 census population
            if pop_nombre_actual and not pop_nombre_actual == '':
              props['esp-ine:poblacion_muni'] = int(pop_poblacion_muni)
            if pop_code_ine_capital and not pop_code_ine_capital == '':
              props['esp-ine:code_ine_capital'] = pop_code_ine_capital
            if pop_capital and not pop_capital == '':
              props['esp-ine:capital'] = pop_capital
            if pop_poblacion_capital and not pop_poblacion_capital == '':
              props['esp-ine:poblacion_capital'] = int(pop_poblacion_capital)
            # this is where other mapping platforms put the label, while we prefer
            # mapshaper for ours, let's carry this along...
            if pop_longitude_etrs89 and not pop_longitude_etrs89 == '':
              props['esp-ine:longitude_etrs89'] = float(pop_longitude_etrs89)
            if pop_latitude_etrs89 and not pop_latitude_etrs89 == '':
              props['esp-ine:longitude_etrs89'] = float(pop_latitude_etrs89)

          # map new props and geom and export default feature
          new_feature['properties'] = props
          new_feature['geometry'] = new_geom

          exporter.export_feature(new_feature)

          # print str(props['wof:id']) + ' is done.'
          feature_cursor += 1