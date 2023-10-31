# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import requests
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

def generate_id():

    url = 'https://api.brooklynintegers.com/rest/'
    params = {'method':'brooklyn.integers.create'}

    try :
        rsp = requests.post(url, params=params)
        data = rsp.content
    except Exception, e:
        logging.error(e)
        return 0

    try:
        data = json.loads(data)
    except Exception, e:
        logging.error(e)
        return 0

    return data.get('integer', 0)

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
    # TIP: comment this out for easier print logging during dev debug
    #sys.stdout.flush()

    # example data record
    # <<snip>>

    geojson_props = row['properties']

    id           = geojson_props['wof_id']
    repo         = geojson_props['wof_repo']
    action       = geojson_props['wof_action']
    src          = geojson_props['wof_src']

    # when setting new records up
    country      = geojson_props['wof_country']

    new_geom = row['geometry']

    # for new and updated records, also set lbl and rev:geo points
    # latitude/longitude values of each geometry's inner centroid
    # can be calculated using Mapshaper
    # see: https://github.com/mbloch/mapshaper
    mps_long     = float( geojson_props['mps_long'] )
    mps_lat      = float( geojson_props['mps_lat'] )

    lgd_name = ''
    lgd_code = ''

    src_name = ''
    area_description = ''
    census_code = ''
    src_type = ''

    name_eng         = ''
    placetype_eng    = ''
    placetype_cym    = ''
    placetype_gla    = ''
    label_eng        = ''
    label_eng_variant = ''
    label_gla        = ''
    name_cym         = ''
    name_gla         = ''
    name_gle         = ''

    supercedes       = []
    inception        = ''


    # Northern Ireland
    if 'LGDNAME' in geojson_props:
      lgd_name         = geojson_props['LGDNAME']
    if 'LGDCode' in geojson_props:
      lgd_code         = geojson_props['LGDCode']

    # England, Wales, Scotland
    if 'Name' in geojson_props:
      src_name         = geojson_props['Name']

    if 'Area_Description' in geojson_props:
      area_description = geojson_props['Area_Description']
    if 'Census_Code' in geojson_props:
      census_code      = geojson_props['Census_Code']
    if 'type' in geojson_props:
      src_type         = geojson_props['type']

    if 'name_eng' in geojson_props:
      name_eng         = geojson_props['name_eng']
    # enforce WOF convention that placetypes are all lowercase
    if 'placetype_eng' in geojson_props:
      placetype_eng    = geojson_props['placetype_eng'].lower()
    # this column was added as NULL strings instead of empty strings
    if 'placetype_cym' in geojson_props and geojson_props['placetype_cym']:
      placetype_cym    = geojson_props['placetype_cym'].lower()
    # this column was added as NULL strings instead of empty strings
    if 'placetype_gla' in geojson_props and geojson_props['placetype_gla']:
      placetype_gla    = geojson_props['placetype_gla'].lower()
    if 'label_eng' in geojson_props:
      label_eng        = geojson_props['label_eng']
    if 'label_eng_variant' in geojson_props:
      label_eng_variant = geojson_props['label_eng_variant']
    if 'label_gla' in geojson_props:
      label_gla        = geojson_props['label_gla']
    if 'name_cym' in geojson_props:
      name_cym         = geojson_props['name_cym']
    if 'name_gla' in geojson_props:
      name_gla         = geojson_props['name_gla']
    if 'name_gle' in geojson_props:
      name_gle         = geojson_props['name_gle']

    if 'supercedes' in geojson_props:
      supercedes_raw         = geojson_props['supercedes']
      supercedes = []
      # these are comma separated WOF ID ints
      if supercedes_raw and not supercedes_raw == '':
        if isinstance(supercedes_raw, int):
          supercedes = [supercedes_raw]
        else:
          for x in supercedes_raw.split(','):
            supercedes.push( int(x.strip()) )

    # when setting new records up
    if 'inception' in geojson_props:
      inception         = geojson_props['wof_inception']

    output = basepath + "/" + repo + "/data/"
    exporter = mapzen.whosonfirst.export.flatfile(output)

    if not id:
      # we assume a new WOF feature needs to be created, with a script generated new ID
      if action == 'new WOF county' or action == 'new macrocounty' or action == 'new county ID':
          # we're not loading in a new feature, we're creating one from scratch this time...
          new_feature = {
              "type":        "Feature",
              "properties":  {},
              "bbox":        {},
              "geometry":    new_geom
          }

          # create variables for existing props and geom to store later (geom moves to alt)
          props = new_feature['properties']

          new_id = generate_id()
          props['wof:id'] = new_id

          # placetype
          if action == 'new WOF county':
            props['wof:placetype'] = 'county'
            props['lbl:min_zoom'] = 10.0
          elif action == 'new macrocounty':
            props['wof:placetype'] = 'macrocounty'
            props['lbl:min_zoom'] = 8.0
          elif action == 'new county ID':
            props['wof:placetype'] = 'county'
            props['lbl:min_zoom'] = 10.0
          else:
            props['wof:placetype'] = placetype
            props['lbl:min_zoom'] = 10.0

          props['wof:supersedes'] = []

          # dont' leave dangling references to expired features on coterminous features
          for superseded_feature_id in supercedes:
            changed = False

            superseded_feature = mapzen.whosonfirst.utils.load(output, superseded_feature_id)
            superseded_props = superseded_feature['properties']

            # a feeature might be not current and superceded into multiple new features
            # so we don't test for current here

            superseded_props['mz:is_current'] = 0
            superseded_props['edtf:superseded'] = '2023-10-25'

            # WARNING: Ensure id is an int (not string) for this test
            if new_id not in superseded_props['wof:superseded_by']:
              superseded_props['wof:superseded_by'].append(new_id)

              changed = True

            # export superseded features
            if changed:
              exporter.export_feature(superseded_feature)

            # concordances were sometimes added to macroregions in error
            # ensure those copied to lower placetype levels (when coterminous)
            #
            # WARNING: This should always have manual review after!
            #
            props['wof:concordances'] = {}

            for concordance_key, concordance_value in superseded_props['wof:concordances'].items():
              if not concordance_key in props['wof:concordances']:
                props['wof:concordances'][concordance_key] = concordance_value

            props['wof:supersedes'].append(superseded_feature_id)

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
          props['src:geom'] = src
          props['wof:geom'] = src
          # may need to update these values if mapshaper is not being used
          props['src:lbl_centroid'] = 'mapshaper'

          # lbl and mps lat/longs
          props['lbl:latitude'] = mps_lat
          props['lbl:longitude'] = mps_long

          # may need to update these values if mapshaper is not being used
          props['mps:latitude'] = mps_lat
          props['mps:longitude'] = mps_long

          # for all the placetypes,set os prefixed properties
          # this is also a concordance value
          if src_name and not src_name == '':
            props[src + ':name'] = src_name
          if area_description and not area_description == '':
            props[src + ':area_description'] = area_description
          if census_code and not census_code == '':
            props[src + ':census_code'] = census_code
            if 'wof:concordances' in props:
              concordances = props.get('wof:concordances', {})
              concordances[src + ':census_code'] = census_code
            else:
              props['wof:concordances'] = {src + ':census_code': census_code}
            props['wof:concordances_official'] = src + ':census_code'
          if src_type and not src_type == '':
            props[src + ':wof_type'] = src_type

          #eng names
          if name_eng and not name_eng == '':
            props['name:eng_x_preferred'] = [name_eng]
            props['wof:name'] = name_eng

          #eng placetype
          if placetype_eng and not placetype_eng == '':
            props['label:eng_x_preferred_placetype'] = [placetype_eng]

          #cym placetype
          if placetype_cym and not placetype_cym == '':
            props['label:cym_x_preferred_placetype'] = [placetype_cym]

          #gla placetype
          if placetype_gla and not placetype_gla == '':
            props['label:gla_x_preferred_placetype'] = [placetype_gla]

          #eng label
          if label_eng and not label_eng == '':
            props['label:eng_x_preferred_longname'] = [label_eng]

          #eng label variant
          if label_eng_variant and not label_eng_variant == '':
            props['label:eng_x_variant_longname'] = [label_eng_variant]

          #gla label
          if label_gla and not label_eng == '':
            props['label:gla_x_preferred_longname'] = [label_gla]

          #cym names
          if name_cym and not name_cym == '':
            props['name:cym_x_preferred'] = [name_cym]

          #gla names
          if name_gla and not name_gla == '':
            props['name:gla_x_preferred'] = [name_gle]

          #gle names
          if name_gle and not name_gle == '':
            props['name:gle_x_preferred'] = [name_gle]

          exporter.export_feature(new_feature)

          # print str(props['wof:id']) + ' is done.'
          feature_cursor += 1
    else:
      # we're trying to load and modify existing WOF features
      feature = mapzen.whosonfirst.utils.load(output, id)

      # guard against bogus WOF ids not matching any feature
      if feature:

        # if a valid wof:id is provided...
        if not id in ["", None]:
          feature = mapzen.whosonfirst.utils.load(output, id)

          # load the feature, pull out props and geom
          props = feature['properties']
          geom =  feature['geometry']

          # set src if unknown
          if not 'src:geom' in props:
            props['src:geom'] = 'unknown'

          if action == 'set macroregion revgeo':
            # create a new alt file
            alt_geom_feature = {'type': 'Feature'}

            # TODO: This should generate a named file with '-reversegeo' postfixed at the end
            # but it does not!? So manual cleanup...
            alt_geom_feature['properties'] = {
                'wof:id': props.get('wof:id'),
                'src:geom': src,
                'src:alt_label': 'reversegeo',
                'wof:repo': repo #,
                #'wof:geomhash': props.get('wof:geomhash')
            }

            # and use old geom variable as new alt geom, export
            alt_geom_feature['geometry'] = new_geom

            # export alt
            # WARNING: order is important here... as we change the value of
            # props['src:geom'] later but because Python vars (especially in objects)
            # are interned (pointers) and we later change the pointer's value
            exporter.export_alt_feature(alt_geom_feature, source=alt_geom_feature['properties']['src:geom'])

            props['reversegeo:geometry'] = str(props.get('wof:id')) + '-alt-' + src + '-reversegeo.geojson'

            # update src and wof props
            # (assumes a "simple" alt geom versus a "source-usage" alt geom)
            if 'src:geom_alt' in props:
              props['src:geom_alt'].append(props['src:geom'])
              # ensure no duplicates
              props['src:geom_alt'] = list(dict.fromkeys(props['src:geom_alt']))
            else:
              props['src:geom_alt'] = [props['src:geom']]

            # this is needed because we always want to list out the explicate,
            # fully qualified "source-usage" alt geom names... while src:geom_alt only
            # lists the source prefixes
            if 'wof:geom_alt' in props:
              props['wof:geom_alt'].append(src + '-reversegeo')
              # ensure no duplicates
              props['wof:geom_alt'] = list(dict.fromkeys(props['wof:geom_alt']))
            else:
              props['wof:geom_alt'] = [src + '-reversegeo']

            # export feature (to add linkage)
            exporter.export_feature(feature)
          else:
            if not action ==  'dupe to new region, deprecate county, update region' and not action == 'dupe to new region, update region, and deprecate county':
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
              props['src:geom'] = src

            if action ==  'dupe to new region, deprecate county, update region' or action == 'dupe to new region, update region, and deprecate county':
              new_id = generate_id()

              # it's bunk now
              props['wof:superseded_by'] = [new_id]
              props['edtf:superseded'] = '2023-10-25'
              props['mz:is_current'] = 0

              # export feature
              exporter.export_feature(feature)

            # now back to setting props on "new" feature...
            props['mz:is_current'] = 1
            props['wof:superseded_by'] = []
            props['edtf:superseded'] = 'uuuu'

            if not inception == '':
              props['edtf:inception'] = inception

            # may need to update these values if mapshaper is not being used
            props['mps:latitude'] = mps_lat
            props['mps:longitude'] = mps_long

            if src_name and not src_name == '':
              props[src + ':name'] = src_name
            if area_description and not area_description == '':
              props[src + ':area_description'] = area_description

            if census_code and not census_code == '':
              props[src + ':census_code'] = census_code
              if 'wof:concordances' in props:
                concordances = props.get('wof:concordances', {})
                concordances[src + ':census_code'] = census_code
              else:
                props['wof:concordances'] = {src + ':census_code': census_code}

              if 'wof:concordances_official' in props:
                if props.has_key('wof:concordances_official_alt'):
                  if not src + ':census_code' in props['wof:concordances_official_alt']:
                    props['wof:concordances_official_alt'].append(props['wof:concordances_official'])
                else:
                  props['wof:concordances_official_alt'] = props['wof:concordances_official']

                props['wof:concordances_official'] = src + ':census_code'
              else:
                props['wof:concordances_official'] = src + ':census_code'

            if src_type and not src_type == '':
              props[src + ':wof_type'] = src_type

            # Northern Ireland specific
            if lgd_name and not lgd_name == '':
              props[src + ':lgd_name'] = lgd_name

            if lgd_code and not lgd_code == '':
              props[src + ':lgd_code'] = lgd_code
              if 'wof:concordances' in props:
                concordances = props.get('wof:concordances', {})
                concordances[src + ':lgd_code'] = lgd_code
              else:
                props['wof:concordances'] = {src + ':lgd_code': lgd_code}
              props['wof:concordances_official'] = src + ':lgd_code'

            #eng names
            if name_eng and not name_eng == '':
              if props.has_key('name:eng_x_preferred'):
                existing_name = props['name:eng_x_preferred'][0]
                existing_wof_name = props['wof:name']

                if not existing_name == name_eng:
                  if existing_name == existing_wof_name:
                    props['wof:name'] = name_eng

                  if props.has_key('name:eng_x_variant'):
                    if not existing_wof_name in props['name:eng_x_variant']:
                      props['name:eng_x_variant'].append(existing_wof_name)

                  props['name:eng_x_preferred'] = [name_eng]
              else:
                props['name:eng_x_preferred'] = [name_eng]
                props['wof:name'] = name_eng

            #eng placetype
            if placetype_eng and not placetype_eng == '':
              if props.has_key('label:eng_x_preferred_placetype'):
                # this is a single element list, because WOF
                existing_val = props['label:eng_x_preferred_placetype'][0]

                if not existing_val == placetype_eng:
                  props['label:eng_x_preferred_placetype'] = [placetype_eng]
                  if props.has_key('label:eng_x_variant_placetype'):
                    if not existing_name in props['label:eng_x_variant_placetype']:
                      props['label:eng_x_variant_placetype'].append(existing_val)
                  else:
                    props['label:eng_x_variant_placetype'] = [existing_val]
              else:
                props['label:eng_x_preferred_placetype'] = [placetype_eng]

            #cym placetype
            if placetype_cym and not placetype_cym == '':
              if props.has_key('label:cym_x_preferred_placetype'):
                # this is a single element list, because WOF
                existing_val = props['label:cym_x_preferred_placetype'][0]

                if not existing_val == placetype_cym:
                  props['label:cym_x_preferred_placetype'] = [placetype_cym]
                  if props.has_key('label:cym_x_variant_placetype'):
                    if not existing_val in props['label:cym_x_variant_placetype']:
                      props['label:cym_x_variant_placetype'].append(existing_val)
                  else:
                    props['label:cym_x_variant_placetype'] = [existing_val]
              else:
                props['label:cym_x_preferred_placetype'] = [placetype_cym]

            #gla placetype
            if placetype_gla and not placetype_gla == '':
              if props.has_key('label:gla_x_preferred_placetype'):
                # this is a single element list, because WOF
                existing_name = props['label:gla_x_preferred_placetype'][0]
                props['label:gla_x_preferred_placetype'] = [placetype_gla]
                if props.has_key('label:gla_x_variant_placetype'):
                  if not existing_name in props['label:gla_x_variant_placetype']:
                    props['label:gla_x_variant_placetype'].append(existing_name)
                else:
                  props['label:gla_x_variant_placetype'] = [existing_name]
              else:
                props['label:gla_x_preferred_placetype'] = [placetype_gla]

            #eng label
            if label_eng and not label_eng == '':
              if props.has_key('label:eng_x_preferred_longname'):
                existing_name = props['label:eng_x_preferred_longname'][0]

                if not existing_name == label_eng:
                  props['label:eng_x_preferred_longname'] = [label_eng]
                  if props.has_key('label:eng_x_variant_longname'):
                    if not existing_name in props['label:eng_x_variant_longname']:
                      props['label:eng_x_variant_longname'].append(existing_name)
                  else:
                    if not existing_name == label_eng:
                      props['label:eng_x_variant_longname'] = [existing_name]
              else:
                props['label:eng_x_preferred_longname'] = [label_eng]

            #eng label variant
            if label_eng_variant and not label_eng_variant == '':
              if props.has_key('label:eng_x_variant_longname'):
                if label_eng_variant not in props['label:eng_x_variant_longname']:
                  props['label:eng_x_variant_longname'].append(label_eng_variant)
              else:
                props['label:eng_x_variant_longname'] = [label_eng_variant]

            #gla label
            if label_gla and not label_gla == '':
              if props.has_key('label:gla_x_preferred_longname'):
                existing_name = props['label:gla_x_preferred_longname'][0]
                props['label:gla_x_preferred_longname'] = [label_gla]
                if props.has_key('label:gla_x_variant_longname'):
                  if not existing_name in props['label:gla_x_variant_longname']:
                    props['label:gla_x_variant_longname'].append(existing_name)
                else:
                  if not existing_name == label_gla:
                    props['label:gla_x_variant_longname'] = [existing_name]
              else:
                props['label:gla_x_preferred_longname'] = [label_gla]

            #cym names
            if name_cym and not name_cym == '':
              if props.has_key('name:cym_x_preferred'):
                existing_name = props['name:cym_x_preferred'][0]
                props['name:cym_x_preferred'] = name_cym
                if props.has_key('name:cym_x_variant'):
                  if not existing_name in props['name:cym_x_variant']:
                    props['name:cym_x_variant'].append(existing_name)
              else:
                props['name:cym_x_preferred'] = [name_cym]

            #gla names
            if name_gla and not name_gla == '':
              if props.has_key('name:gla_x_preferred'):
                existing_name = props['name:gla_x_preferred'][0]
                props['name:gla_x_preferred'] = name_gla
                if props.has_key('name:gla_x_variant'):
                  if not existing_name in props['name:gla_x_variant']:
                    props['name:gla_x_variant'].append(existing_name)
              else:
                props['name:gla_x_preferred'] = [name_gle]

            #gle names
            if name_gle and not name_gle == '':
              if props.has_key('name:gle_x_preferred'):
                existing_name = props['name:gle_x_preferred'][0]
                props['name:gle_x_preferred'] = name_gle
                if props.has_key('name:gle_x_variant'):
                  if not existing_name in props['name:gle_x_variant']:
                    props['name:gle_x_variant'].append(existing_name)
              else:
                props['name:gle_x_preferred'] = [name_gle]

            # set centroids
            # nvkelso (20231025) - Turns out these weren't set yet (so not overriding custom values)
            props['lbl:latitude'] = mps_lat
            props['lbl:longitude'] = mps_long

            # may need to update these values if mapshaper is not being used
            props['src:lbl_centroid'] = 'mapshaper'

            if action == 'update macroregion':
              # we already set the alt geom dance, so nothing more

              # export feature
              exporter.export_feature(feature)
            # create new feature using old's props but new geom
            elif action ==  'dupe to new region, deprecate county, update region' or action == 'dupe to new region, update region, and deprecate county':
              new_feature = {
                  "type":        "Feature",
                  "properties":  props,
                  "bbox":        {},
                  "geometry":    new_geom
              }

              # now that we won't corrupt the existing feature's properties, because python

              props['wof:id'] = new_id

              # since this is a new features, clear out superseded_by and supersedes
              props['wof:supersedes'] = [id]
              props['wof:superseded_by'] = []

              # since we're doing coterminous features now, no need for placetype_alt
              if props.has_key('wof:placetype_alt'):
                del props['wof:placetype_alt']

              # we verified these are all current, so flag
              props['mz:hierarchy_label'] = 1

              # placetype
              props['wof:placetype'] = 'region'

              # we're not copying over alt geoms, so null those out
              if props.has_key('src:geom_alt'):
                del props['src:geom_alt']
              if props.has_key('wof:geom_alt'):
                del props['wof:geom_alt']

              # reset parent and hierarchy (needs PIP)
              props['wof:parent_id'] = -1
              props['wof:hierarchy'] = {}

              # export coterminous feature
              exporter.export_feature(new_feature)

            # new record (but not an alt)
            # we're not loading in a new feature, we're creating one from scratch this time...
            elif action == 'update region and dupe to new county' or action == 'update borough and dupe into new coterminous county' or action == 'update county and dupe to new region':
              new_feature = {
                  "type":        "Feature",
                  "properties":  props,
                  "bbox":        {},
                  "geometry":    new_geom
              }

              new_id = generate_id()

              # set existing feature coterminous to new feature
              if props.has_key('wof:coterminous'):
                if not new_id in props['wof:coterminous']:
                    props['wof:coterminous'].append(new_id)
              else:
                props['wof:coterminous'] = [new_id]

              if not action == 'update borough and dupe into new coterminous county':
                # since we're doing coterminous features now, no need or placetype_alt
                if props.has_key('wof:placetype_alt'):
                  del props['wof:placetype_alt']

              # we verified these are all current, so flag
              props['mz:is_current'] = 1
              props['wof:superseded_by'] = []
              props['edtf:superseded'] = 'uuuu'

              # placetype
              if action == 'update region and dupe to new county':
                props['mz:hierarchy_label'] = 1
              elif action == 'update borough and dupe into new coterminous county':
                props['mz:hierarchy_label'] = 1
              elif action == 'update county and dupe to new region':
                props['mz:hierarchy_label'] = 0
              else:
                props['mz:hierarchy_label'] = 0

              # export feature
              exporter.export_feature(feature)

              # now that we won't corrupt the existing feature's properties, because python

              props['wof:id'] = new_id

              # placetype
              if action == 'update region and dupe to new county':
                props['wof:placetype'] = 'county'
                props['mz:hierarchy_label'] = 0
              elif action == 'update borough and dupe into new coterminous county':
                props['wof:placetype'] = 'county'
                props['mz:hierarchy_label'] = 0
              elif action == 'update county and dupe to new region':
                props['wof:placetype'] = 'region'
                props['mz:hierarchy_label'] = 1
              else:
                props['mz:hierarchy_label'] = 1

              # reverse: set new feature coterminous to the existing feature
              if props.has_key('wof:coterminous'):
                if not id in props['wof:coterminous']:
                    props['wof:coterminous'].append(id)

                # make sure we don't have our new records ID be self ref
                props['wof:coterminous'].remove(new_id)
              else:
                props['wof:coterminous'] = [id]

              # since this is a new features, clear out superseded_by and supersedes
              props['wof:superseded_by'] = []
              props['wof:supersedes'] = []

              # we're not copying over alt geoms, so null those out
              if props.has_key('src:geom_alt'):
                del props['src:geom_alt']
              if props.has_key('wof:geom_alt'):
                del props['wof:geom_alt']

              # reset parent and hierarchy (needs PIP)
              props['wof:parent_id'] = -1
              props['wof:hierarchy'] = {}

              # export coterminous feature
              exporter.export_feature(new_feature)


            # print str(props['wof:id']) + ' is done.'
            feature_cursor += 1