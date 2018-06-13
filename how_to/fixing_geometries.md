# Validating geometries

## Proof of concept

The following has been tested and shown to work on a limited set of Who's On First documents but should not be treated as anything "production" ready.

```
#!/usr/bin/env python

# in addition to shapely this depends on both these,
# which need to be installed by hand at least as of
# this writing (20180503/thisisaaronland)
#
# https://libspatialindex.github.io/ - required by the (python) rtree library which is required by makevalid
# https://github.com/ftwillms/makevalid

import os
import logging
import sys

import json
import geojson
import makevalid

import mapzen.whosonfirst.utils
import mapzen.whosonfirst.export

from shapely.geometry import asShape

if __name__ == "__main__":

    import optparse
    opt_parser = optparse.OptionParser()
    
    opt_parser.add_option('-d', '--debug', dest='debug', action='store_true', default=False, help='...')
    opt_parser.add_option('-v', '--verbose', dest='verbose', action='store_true', default=False, help='Be chatty (default is false)')

    options, args = opt_parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    for repo in args:

        repo = os.path.abspath(repo)
        data = os.path.join(repo, "data")

        exporter = mapzen.whosonfirst.export.flatfile(data)
        crawl = mapzen.whosonfirst.utils.crawl(data, inflate=True)
        
        for feature in crawl:

            props = feature["properties"]
            shp = asShape(feature["geometry"])

            vshp = makevalid.make_geom_valid(shp)

            if not vshp:
                logging.warning("failed to make a valid shape for %s" % props["wof:id"])
                continue

            if shp == vshp:
                logging.debug("original shape and validated shape are the same for %s" % props["wof:id"])
                continue

            if options.debug:
                logging.info("update shape for %s (but don't because debugging is enabled)" % props["wof:id"])
                continue

            feature["geometry"] = vshp

            # please tell me there's a better way to do this... no, really
            # please tell me - I want to know (20180503/thisisaaronland)

            feature = json.loads(geojson.dumps(feature))

            logging.info(exporter.export_feature(feature))
```
