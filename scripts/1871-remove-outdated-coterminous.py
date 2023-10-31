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

    changed = False

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
              if 'wof:coterminous' in props:
                for coterminous_id in props['wof:coterminous']:
                  try:
                    coterminous_feature = mapzen.whosonfirst.utils.load(output, coterminous_id)

                    coterminous_props = coterminous_feature['properties']

                    if coterminous_props['mz:is_current'] == 0:
                      # since the localadmin is now deprecated, and the locality supersedes it
                      # lets remove it from locality's list of coterminous features
                      props['wof:coterminous'].remove(coterminous_id)
                      changed = True

                    else:
                      sys.stdout.write('\rProblem with WOF ID = {} in repo {} to load coterminous feature for {}...\r'.format(coterminous_id,repo,id))
                  except:
                    sys.stdout.write('\rProblem with WOF ID = {} in repo {} to load coterminous feature for {}...\r'.format(coterminous_id,repo,id))

                if len(props['wof:coterminous']) == 0:
                  del props['wof:coterminous']

                # export features
                if changed:
                  exporter.export_feature(feature)

              # print str(props['wof:id']) + ' is done.'
              row_cursor += 1