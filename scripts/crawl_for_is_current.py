#stepps00 - 05.18.2018
#for tagging records as current

import mapzen.whosonfirst.utils
import mapzen.whosonfirst.export

if __name__ == "__main__":

    data = "/path/to/whosonfirst-data/data/"
    crawl = mapzen.whosonfirst.utils.crawl(data, inflate=True)
    exporter = mapzen.whosonfirst.export.flatfile(data)

    for feature in crawl:

        update = False
        props = feature['properties']

        #check for any non-null cessation
        if props.has_key('edtf:cessation'):
            if not props['edtf:cessation'] == 'uuuu':
                if not props['edtf:cessation'] == '':
                    props['mz:is_current'] = 0
                    update = True

        #check for any non-null deprecated
        if props.has_key('edtf:deprecated'):
            if props.has_key('edtf:deprecated') == 'uuuu':
                if props.has_key('edtf:deprecated') == '':
                    props['mz:is_current'] = 0
                    update = True

        #check for any non-null superseded_by
        if props.has_key('wof:superseded_by'):
            if not props['wof:superseded_by'] == []:
                if not props['wof:superseded_by'] == [""]:
                    props['mz:is_current'] = 0
                    update = True

        if update:
            exporter.export_feature(feature)
            print props['wof:id']