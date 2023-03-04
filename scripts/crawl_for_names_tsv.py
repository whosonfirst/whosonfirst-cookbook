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
    print 'iso\tid\tname\teng\tben\tguj\thin\tkan\tmal\tmar\tpan\ttam\ttel\turd\tv_eng\tv_ben\tv_guj\tv_hin\tv_kan\tv_mal\tv_mar\tv_pan\tv_tam\tv_tel\tv_urd'

    for iso in isos:

        data = "/path/to/whosonfirst-data-admin-" + iso + "/data/"
        crawl = mapzen.whosonfirst.utils.crawl(data, inflate=True)
        exporter = mapzen.whosonfirst.export.flatfile(data)

        #check all features
        for feature in crawl:

            #set up vars for each pref name
            name = ''
            eng = ''
            ben = ''
            guj = ''
            hin = ''
            kan = ''
            mal = ''
            mar = ''
            pan = ''
            tam = ''
            tel = ''
            urd = ''

            #set up vars for each variant name
            v_eng = ''
            v_ben = ''
            v_guj = ''
            v_hin = ''
            v_kan = ''
            v_mal = ''
            v_mar = ''
            v_pan = ''
            v_tam = ''
            v_tel = ''
            v_urd = ''

            props = feature['properties']

            try:
                #only operate on "current" records
                is_curr = -1

                if 'mz:is_current' in props:
                    is_curr = int(props['mz:is_current'])

                if not is_curr == 0:
                    #map each pref name
                    if 'wof:name' in props:
                        name = props['wof:name']
                    if 'name:eng_x_preferred' in props:
                        eng = props['name:eng_x_preferred'][0]
                    if 'name:ben_x_preferred' in props:
                        ben = props['name:ben_x_preferred'][0]
                    if 'name:guj_x_preferred' in props:
                        guj = props['name:guj_x_preferred'][0]
                    if 'name:hin_x_preferred' in props:
                        hin = props['name:hin_x_preferred'][0]
                    if 'name:kan_x_preferred' in props:
                        kan = props['name:kan_x_preferred'][0]
                    if 'name:mal_x_preferred' in props:
                        mal = props['name:mal_x_preferred'][0]
                    if 'name:mar_x_preferred' in props:
                        mar = props['name:mar_x_preferred'][0]
                    if 'name:pan_x_preferred' in props:
                        pan = props['name:pan_x_preferred'][0]
                    if 'name:tam_x_preferred' in props:
                        tam = props['name:tam_x_preferred'][0]
                    if 'name:tel_x_preferred' in props:
                        tel = props['name:tel_x_preferred'][0]
                    if 'name:urd_x_preferred' in props:
                        urd = props['name:urd_x_preferred'][0]

                    #map each variant name
                    if 'name:eng_x_variant' in props:
                        v_eng = ', '.join(props['name:eng_x_variant'])
                    if 'name:ben_x_variant' in props:
                        v_ben = ', '.join(props['name:ben_x_variant'])
                    if 'name:guj_x_variant' in props:
                        v_guj = ', '.join(props['name:guj_x_variant'])
                    if 'name:hin_x_variant' in props:
                        v_hin = ', '.join(props['name:hin_x_variant'])
                    if 'name:kan_x_variant' in props:
                        v_kan = ', '.join(props['name:kan_x_variant'])
                    if 'name:mal_x_variant' in props:
                        v_mal = ', '.join(props['name:mal_x_variant'])
                    if 'name:mar_x_variant' in props:
                        v_mar = ', '.join(props['name:mar_x_variant'])
                    if 'name:pan_x_variant' in props:
                        v_pan = ', '.join(props['name:pan_x_variant'])
                    if 'name:tam_x_variant' in props:
                        v_tam = ', '.join(props['name:tam_x_variant'])
                    if 'name:tel_x_variant' in props:
                        v_tel = ', '.join(props['name:tel_x_variant'])
                    if 'name:urd_x_variant' in props:
                        v_urd = ', '.join(props['name:urd_x_variant'])

                #print id and names, one record per row
                print iso + '\t' + str(props['wof:id']) + '\t' + name + '\t' + eng + '\t' + ben + '\t' + guj + '\t' + hin + '\t' + kan + '\t' + mal + '\t' + mar + '\t' + pan + '\t' + tam + '\t' + tel + '\t' + urd + '\t' + v_eng + '\t' + v_ben + '\t' + v_guj + '\t' + v_hin + '\t' + v_kan + '\t' + v_mal + '\t' + v_mar + '\t' + v_pan + '\t' + v_tam + '\t' + v_tel + '\t' + v_urd

            except:
                print "Error: " + str(props['wof:id'])