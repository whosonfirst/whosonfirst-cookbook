#stepps00 - 05.18.2018
#for listing out existing concordance sources

import mapzen.whosonfirst.utils
import mapzen.whosonfirst.export

if __name__ == "__main__":

    data = "/path/to/whosonfirst-data/data/"
    crawl = mapzen.whosonfirst.utils.crawl(data, inflate=True)
    exporter = mapzen.whosonfirst.export.flatfile(data)

    #empty list of concordances
    concordances = []

    for feature in crawl:

        props = feature['properties']

        for prop in props:
            if props.has_key('wof:concordances'):
                existing_concordance_list = props['wof:concordances']

                #found concordances, now split each concordance to get each prefix
                for value in existing_concordance_list:
                    concordance_prefix = value.rsplit(':')[0]

                    #now append prefixes to the concordances list
                    if not concordance_prefix in concordances:
                        concordances.append(concordance_prefix)
                        print str(concordance_prefix) + ' appended to the list..'

    #print all concordances
    print concordances