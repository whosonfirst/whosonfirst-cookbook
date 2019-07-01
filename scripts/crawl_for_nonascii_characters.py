# -*- coding: UTF-8 -*-
import sys
import mapzen.whosonfirst.utils

if __name__ == "__main__":

    data = "/path/to/whosonfirst-data-admin-*/data/"
    crawl = mapzen.whosonfirst.utils.crawl(data, inflate=True)

    def isascii(x):
        try:
            x.encode(encoding='utf-8').decode('ascii')
        except UnicodeDecodeError:
            return False
        else:
            return True

    for feature in crawl:
        props = feature['properties']
        if not isascii(props['wof:name']):
            print str(props['wof:id']) + '\t' + props['wof:name']
