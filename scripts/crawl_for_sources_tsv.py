# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import mapzen.whosonfirst.utils
import mapzen.whosonfirst.export
import optparse

if __name__ == "__main__":

    #crawl each admin repo
    isos = ['jp','ch','me','ca','gb','mx','ro','ad','fi','gw','cz','ms','xs','au','lv','rs','ae','gy','no','fj','ci','ly','um','ck','iq','sm','xk','cy','mr','xn','uk','aw','ps','th','tj','np','fk','nr','fm','bn','kp','ma','cl','un','mc','nu','fo','nz','bo','mt','ir','sn','ax','is','gu','jo','bd','am','sd','ht','lb','bw','to','la','sc','hr','al','bt','tn','kz','sb','hn','st','pa','jm','bb','ss','bs','tm','ga','ky','br','je','ba','om','fr','ai','sa','ag','rw','hk','af','sr','it','ru','ye','tl','kw','bq','tk','kr','mw','dm','xz','mv','dk','xy','az','so','mu','dj','xx','hm','dn','us','tr','se','cm','de','md','uy','pe','gd','pf','by','lc','tt','ge','bz','li','tu','pg','gf','sx','bf','ke','sy','lk','sv','hu','be','an','tv','cc','bg','kg','bh','lr','tc','bi','kh','ki','tw','ph','gg','td','bj','km','bl','kn','tg','bm','ko','cd','yt','ls','tz','do','cf','sz','tf','my','lt','za','dz','ua','cg','lu','mz','ug','zm','pk','ec','na','zw','gh','ee','nc','eg','id','sg','ne','eh','nf','er','ao','ie','sh','aq','il','pl','gi','pm','gl','pn','gm','si','pr','gn','ar','im','sj','as','gp','ng','pt','gq','pw','gr','py','gs','qa','gt','re','es','ni','et','nl','cn','uz','mq','cx','ws','mp','cw','wf','mo','cv','vu','mn','cu','vn','mm','sl','io','at','cr','vi','ml','sk','in','vg','mk','ve','mh','vc','mg','va','mf','co']

    #headers
    print 'iso\tsources'

    for iso in isos:

        data = "/path/to/whosonfirst-data-admin-" + iso + "/data/"
        crawl = mapzen.whosonfirst.utils.crawl(data, inflate=True)
        exporter = mapzen.whosonfirst.export.flatfile(data)

        #set up var
        sources = []

        #check all features
        for feature in crawl:

            props = feature['properties']

            try:
                #only operate on "current" records
                is_curr = -1

                if 'mz:is_current' in props:
                    is_curr = int(props['mz:is_current'])

                if not is_curr == 0:

                    #map each name
                    if 'src:geom' in props:
                        if not props['src:geom'] in sources:
                            sources.append(props['src:geom'])

            except:
                print "Error: " + str(props['wof:id'])

        #print id and names, one record per row
        print iso + '\t' + str(sources)