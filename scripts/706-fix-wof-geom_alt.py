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

    #wof:id,repo
    #1880559933,es

    id           = row['wof:id']
    repo         = 'whosonfirst-data-admin-' + row['repo']

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

              # sometimes there was a source with multiple usages
              # in that case we should only list the source once
              # FYI: this doesn't sort it, though
              # example: Spain (85633129)
              if 'src:geom_alt' in props:
                props['src:geom_alt'] = list(dict.fromkeys(props['src:geom_alt']))

              # Get the directory for this WOF record
              wof_record_directory = output + '/'.join([id[i:i + 3] for i in range(0, len(id), 3)]) + '/'

              # Get the prefix
              prefix = id + "-alt-"

              # List all the files in the record's directory that are it's fully qualified alt geometry
              files = [file for file in os.listdir(wof_record_directory) if file.startswith(prefix)]

              wof_alts = []
              for file in files:
                # remove the prefix on the file name while constructing the list
                # and remove the .geojoson postfix, too
                wof_alts.append(file[len(prefix):][:-len('.geojson')])

              # to make diffs more predictable, always sort that list
              wof_alts.sort()

              # this is needed because we always want to list out the explicate,
              # fully qualified "source-usage" alt geom names... while src:geom_alt only
              # lists the source prefixes
              # NOTE: it's OK to set a empty list, as this is a core WOF property
              # example: Spain (85633129) or Barcelona (85682663) or Burgos (85682667)
              # or "no territory" (1880559933) with empty list
              props['wof:geom_alt'] = wof_alts

              # export feature
              exporter.export_feature(feature)

              # print str(props['wof:id']) + ' is done.'
              row_cursor += 1