# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os

import mapzen.whosonfirst.utils
import mapzen.whosonfirst.export

if __name__ == "__main__":

    #lookup table to map old iso to new iso codes
    iso_lookup = {
        'alb':'sqi',
        'arm':'hye',
        'baq':'eus',
        'bur':'mya',
        'chi':'zho',
        'cze':'ces',
        'dut':'nld',
        'fre':'fra',
        'geo':'kat',
        'ger':'deu',
        'gre':'ell',
        'ice':'isl',
        'mac':'mkd',
        'mao':'mri',
        'may':'msa',
        'per':'fas',
        'rum':'ron',
        'slo':'slk',
        'tib':'bod',
        'wel':'cym'
    }

    dir = os.getcwd()
    data = dir + "/data/"

    crawl = mapzen.whosonfirst.utils.crawl(data, inflate=True)
    exporter = mapzen.whosonfirst.export.flatfile(data)

    for feature in crawl:

        change = False    

        props = feature['properties']

        #check each kv pair in lookup
        for bad,good in iso_lookup.items():
            #if we have a candidate...
            if props.has_key('name:' + bad + '_x_preferred'):

                change = True

                #in this case, append to existing variant prop
                if props.has_key('name:' + good + '_x_preferred'):
                    if props.has_key('name:' + good + '_x_variant'):
                        for name in props['name:' + bad + '_x_preferred']:
                            if not name in props['name:' + good + '_x_variant']:
                                props['name:' + good + '_x_variant'].append(name)

                    #in this case, move to new variant prop
                    if not props.has_key('name:' + good + '_x_variant'):
                        props['name:' + good + '_x_variant'] = props['name:' + bad + '_x_preferred']

                #in this case, move to new preferred prop
                if not props.has_key('name:' + good + '_x_preferred'):
                    props['name:' + good + '_x_preferred'] = props['name:' + bad + '_x_preferred']

                #then delete bunk iso prop after remap
                del props['name:' + bad + '_x_preferred']

            #but, sometimes we introduce duplicate values
            #so clean up the variant props
            if props.has_key('name:' + good + '_x_preferred'):
                if props.has_key('name:' + good + '_x_variant'):
                    for name in props['name:' + good + '_x_variant']:
                        if name in props['name:' + good + '_x_preferred']:
                            props['name:' + good + '_x_variant'].remove(name)

                    if len(props['name:' + good + '_x_variant']) == 0:
                        del props['name:' + good + '_x_variant']

        #write to disk
        if change:
            exporter.export_feature(feature)
