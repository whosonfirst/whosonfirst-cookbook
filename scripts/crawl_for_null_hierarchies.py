#stepps00 - 05.27.2018
#crawl to find empty hierarchies

import mapzen.whosonfirst.utils
import mapzen.whosonfirst.export

if __name__ == "__main__":

    data = "/path/to/whosonfirst-data/data/"
    crawl = mapzen.whosonfirst.utils.crawl(data, inflate=True)
    exporter = mapzen.whosonfirst.export.flatfile(data)

    for feature in crawl:

        props = feature['properties']

        if props.has_key('wof:hierarchy'):
            #if null, print
            if props['wof:hierarchy'] == []:
                print props['wof:id']

        #or, if no prop, print
        else:
            print props['wof:id']