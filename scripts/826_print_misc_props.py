#stepps00 -06.2018
#find all misc properties

import mapzen.whosonfirst.utils
import mapzen.whosonfirst.export

if __name__ == "__main__":

    data = "/path/to/whosonfirst-data/data/"
    crawl = mapzen.whosonfirst.utils.crawl(data, inflate=True)
    exporter = mapzen.whosonfirst.export.flatfile(data)

    #empty list for later
    misc_props = []

    for feature in crawl:
        props = feature['properties']

        #check each prop
        for prop in props:
            if prop.startswith('misc:'):
                #if the prefix is misc, append it to misc_props list
                if not prop in misc_props:
                    misc_props.append(prop)

    #print em
    print misc_props