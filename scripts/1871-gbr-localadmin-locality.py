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

    #wof:id,repo,placetype
    #1729579505,gb,localadmin

    id           = row['wof:id']
    repo         = 'whosonfirst-data-admin-' + row['repo']

    try:
      action = row['action']
    except:
      action       = ''

    if id:
      output = basepath + "/" + repo + "/data/"
      exporter = mapzen.whosonfirst.export.flatfile(output)

      feature = mapzen.whosonfirst.utils.load(output, id)

      # guard against bogus WOF ids not matching any feature
      if feature:

        # if a valid wof:id is provided...
        if not id in ["", None]:
          feature = mapzen.whosonfirst.utils.load(output, id)

          if feature:
            # load the feature, pull out props and geom
            props = feature['properties']

            # only operate on current features
            if not props['mz:is_current'] == 0:
              if 'label:eng_x_preferred_placetype' in props or 'qs:type' in props:
                # deliberately avoiding (props['qs:type'] == 'Unitary Council' and props['qs:a1r'] == 'Scotland')
                # deliberately avoiding (props['qs:type'] == 'Civil Parish or Community' and props['qs:a1r'] == 'Wales')
                # as we want to keep those both localadmin / manual review for later
                if props['label:eng_x_preferred_placetype'] == 'civil parish' or props['label:eng_x_preferred_placetype'] == 'non-civil parish' or props['qs:type'] == 'Civil Parish or Community'  or props['qs:type'] == 'Non-Civil Parish or Community' or action == 'gore':
                  # manual overrides before regular processing
                  if action == 'supercede':
                    if 'wof:coterminous' in props:
                      props['wof:coterminous'].append(int(row['loc_id']))
                    else:
                      props['wof:coterminous'] = [int(row['loc_id'])]

                  if 'wof:coterminous' in props:
                    for coterminous_id in props['wof:coterminous']:
                      try:
                        coterminous_feature = mapzen.whosonfirst.utils.load(output, coterminous_id)

                        #if coterminous_feature:
                        coterminous_props = coterminous_feature['properties']

                        props['wof:superseded_by'] = [coterminous_id]
                        props['edtf:deprecated'] = '2023-10-10'
                        props['mz:is_current'] = 0
                        if coterminous_props['wof:supersedes']:
                          coterminous_props['wof:supersedes'].append(id)
                        else:
                          coterminous_props['wof:supersedes'] = [id]

                        if coterminous_props['wof:placetype'] == 'locality':
                          # copy over relevant props
                          if 'label:eng_x_preferred_placetype' in props:
                            coterminous_props['label:eng_x_preferred_placetype'] = props['label:eng_x_preferred_placetype']
                          if 'label:fra_x_preferred_placetype' in props:
                            coterminous_props['label:fra_x_preferred_placetype'] = props['label:fra_x_preferred_placetype']
                          if 'label:fra_x_preferred_placetype' in props:
                            coterminous_props['label:fra_x_preferred_placetype'] = props['label:fra_x_preferred_placetype']
                          if 'wof:label' in props:
                            coterminous_props['label:eng_x_preferred_longname'] = props['wof:label']

                        # mostly we're aiming to copy over `gbr-ons:gss_code` concordances...
                        if 'wof:concordances' in props:
                          if 'wof:concordances' in coterminous_props:
                            coterminous_concordances = coterminous_props.get('wof:concordances')
                            for concordance in props['wof:concordances']:
                              # but don't overwrite existing gbr-ons:gss_code concordance! manual review
                              if not concordance in coterminous_concordances:
                                coterminous_concordances[concordance] = props['wof:concordances'][concordance]
                              else:
                                if 'wof:concordances_alts' in coterminous_props:
                                  if concordance in coterminous_props['wof:concordances_alts']:
                                    coterminous_props['wof:concordances_alts'][concordance].append(props['wof:concordances'][concordance])
                                  else:
                                    coterminous_props['wof:concordances_alts'][concordance] = [props['wof:concordances'][concordance]]
                                else:
                                  coterminous_props['wof:concordances_alts'] = {concordance: [props['wof:concordances'][concordance]]}
                          else:
                            coterminous_concordances = props['wof:concordances']

                          # ensure we're tracking 'gbr-ons:gss_code'
                          if 'wof:concordances_official' in props:
                            coterminous_props['wof:concordances_official'] = props['wof:concordances_official']

                          if 'wof:concordances_official_alt' in props:
                            coterminous_props['wof:concordances_official_alt'] = props['wof:concordances_official_alt']

                          # since the localadmin is now deprecated, and the locality supersedes it
                          # lets remove it from locality's list of coterminous features
                          if 'wof:coterminous' in coterminous_props:
                            del coterminous_props['wof:coterminous']

                          # note, there are rare cases when a locality is also a localadmin
                          # those should be reviewed manually, but most should remain that config

                          # export features
                          exporter.export_feature(feature)
                          exporter.export_feature(coterminous_feature)
                        else:
                          sys.stdout.write('\rProblem with WOF ID = {} in repo {} to load coterminous feature for {}...\r'.format(coterminous_id,repo,id))
                      except:
                        sys.stdout.write('\rProblem with WOF ID = {} in repo {} to load coterminous feature for {}...\r'.format(coterminous_id,repo,id))
                  elif 'wof:name' == '':
                    props['edtf:deprecated'] = '2023-10-10'
                    props['mz:is_current'] = 0

                    # export features
                    exporter.export_feature(feature)
                  # There are a few non-civil parish we have to take care of...
                  # deliberately avoiding (props['qs:type'] == 'Unitary Council' and props['qs:a1r'] == 'Scotland')
                  # deliberately avoiding (props['qs:type'] == 'Civil Parish or Community' and props['qs:a1r'] == 'Wales')
                  # as we want to keep those both localadmin / manual review for later
                  elif props['label:eng_x_preferred_placetype'] == 'non-civil parish' or props['qs:type'] == 'urban core' or props['qs:type'] == 'Non-Civil Parish or Community' or action == 'gore':
                    # This should have been set before
                    props['wof:statistical_gore'] = 1

                    new_id = generate_id()

                    props['wof:superseded_by'] = [new_id]
                    props['edtf:deprecated'] = '2023-10-10'
                    props['mz:is_current'] = 0

                    # export features
                    exporter.export_feature(feature)

                    #we're not loading in a new feature, we're creating one from scratch this time...
                    new_feature = {
                        "type":        "Feature",
                        "properties":  props,
                        "bbox":        {},
                        "geometry":    feature['geometry']
                    }

                    new_props = new_feature['properties']

                    # extra gymnastics here because of Python pointers
                    new_props['edtf:deprecated'] = 'uuuu'
                    new_props['hierarchy_label'] = 0
                    new_props['mz:is_current'] = 1
                    new_props['mz:is_funky'] = 1
                    new_props['wof:belongsto'] = []
                    new_props['wof:hierarchy'] = []
                    new_props['wof:id'] = new_id
                    new_props['wof:parent_id'] = -1
                    new_props['wof:placetype'] = 'locality'
                    new_props['wof:superseded_by'] = []
                    new_props['wof:supersedes'] = [id]

                    exporter.export_feature(new_feature)

              # print str(props['wof:id']) + ' is done.'
              row_cursor += 1