#stepps00 - 2020-12-15

#crawl repos to compare records to their parent records
#flagging as coterminous when certain parameters are met

import mapzen.whosonfirst.utils
import mapzen.whosonfirst.export
import Levenshtein

if __name__ == "__main__":
    
    #check country codes
    isos = ['jp','ch','me','ca','gb','mx','ro','ad','fi','gw','cz','ms','xs','au','lv','rs','ae','gy','no','fj','ci','ly','um','ck','iq','sm','xk','cy','mr','xn','uk','aw','ps','th','tj','np','fk','nr','fm','bn','kp','ma','cl','un','mc','nu','fo','nz','bo','mt','ir','sn','ax','is','gu','jo','bd','am','sd','ht','lb','bw','to','la','sc','hr','al','bt','tn','kz','sb','hn','st','pa','jm','bb','ss','bs','tm','ga','ky','br','je','ba','om','fr','ai','sa','ag','rw','hk','af','sr','it','ru','ye','tl','kw','bq','tk','kr','mw','dm','xz','mv','dk','xy','az','so','mu','dj','xx','hm','dn','us','tr','se','cm','de','md','uy','pe','gd','pf','by','lc','tt','ge','bz','li','tu','pg','gf','sx','bf','ke','sy','lk','sv','hu','be','an','tv','cc','bg','kg','bh','lr','tc','bi','kh','ki','tw','ph','gg','td','bj','km','bl','kn','tg','bm','ko','cd','yt','ls','tz','do','cf','sz','tf','my','lt','za','dz','ua','cg','lu','mz','ug','zm','pk','ec','na','zw','gh','ee','nc','eg','id','sg','ne','eh','nf','er','ao','ie','sh','aq','il','pl','gi','pm','gl','pn','gm','si','pr','gn','ar','im','sj','as','gp','ng','pt','gq','pw','gr','py','gs','qa','gt','re','es','ni','et','nl','cn','uz','mq','cx','ws','mp','cw','wf','mo','cv','vu','mn','cu','vn','mm','sl','io','at','cr','vi','ml','sk','in','vg','mk','ve','mh','vc','mg','va','mf','co']

    for iso in isos:

        print ('\t' + str(iso))

        data = "/path/to/wof-data-admin-" + str(iso) + "/data/"
        crawl = mapzen.whosonfirst.utils.crawl(data, inflate=True)
        exporter = mapzen.whosonfirst.export.flatfile(data)

        #check all features
        for feature in crawl:

            #used later to append matches
            matched_records = {}

            #create var for all properties and geom
            props = feature['properties']
            geom = feature['geometry']

            #only operate on "current" records
            is_curr = -1

            if 'mz:is_current' in props:
                is_curr = props['mz:is_current']

            if not is_curr == 0:

                #check some placetypes, but not all
                if props['wof:placetype'] in ['locality', 'localadmin', 'county', 'macrocounty', 'region']:

                    #and only check non-Point geoms
                    if not geom['type'] == 'Point':

                        #for the feature we're checking, we need to know a few things about the record
                        geom_area = props['geom:area']
                        
                        name = props['wof:name']
                        id = props['wof:id']

                        coterm = []
                        if 'wof:coterminous' in props:
                            for i in props['wof:coterminous']:
                                coterm.append(i)

                        #and when available, prefer eng name
                        if 'name:eng_x_preferred' in props:
                            name = str(props['name:eng_x_preferred'][0])
                        
                        hierarchy = props['wof:hierarchy']

                        #now check all hierarchies in wof:hierarchy
                        for hier in hierarchy:

                            #and for each k,v pair, open up the record to compare
                            for p_pt,p_id in hier.items():

                                #skip continents because they arent coterminous and live in XY repo
                                if not p_pt == 'continent_id':

                                    #and skip self and -1 vals
                                    if not int(p_id) in [int(id), -1]:

                                        #catch for parent records that don't live in the same repo
                                        try:
                                            p_feature = {}
                                            p_feature = mapzen.whosonfirst.utils.load(data, p_id)
         
                                        except:
                                            print ('\r')
                                        
                                        #if we actually have a parent record, continue
                                        if not p_feature == {}:
        
                                            #create var for all properties and geom
                                            p_props = p_feature['properties']
                                            p_geom = p_feature['geometry']
        
                                            #only operate on "current" records
                                            is_curr = -1
                                
                                            if 'mz:is_current' in p_props:
                                                is_curr = p_props['mz:is_current']
                                
                                            if not is_curr == 0:
                                                #for the feature we're checking, we need to know a few things about the record
                                                p_geom_area = p_props['geom:area']
        
                                                p_name = p_props['wof:name']

                                                p_coterm = []
                                                if 'wof:coterminous' in p_props:
                                                    for i in p_props['wof:coterminous']:
                                                        p_coterm.append(i)
        
                                                #and when available, prefer eng name
                                                if 'name:eng_x_preferred' in p_props:
                                                    p_name = str(p_props['name:eng_x_preferred'][0])
        
                                                #at this point, compare record and parent record name and area
                                                #if similar enough, append to list above
                                                name_diff = Levenshtein.distance(p_name, name)
        
                                                if name_diff < 2:
                                                    #at this point, weve found "matching" record + parent name
                                                    size_match = False

                                                    #if the difference is within ~15% of the parent geom size, call it a match
                                                    if abs(p_geom_area - geom_area) < (float(p_geom_area) / 6.667):
                                                        size_match = True

                                                    #or if the difference very small, call it a match (helps with QS shape matches)
                                                    if props['wof:placetype'] == 'neighbourhood':
                                                        if abs(p_geom_area - geom_area) < .002:
                                                            size_match = True

                                                    if size_match == True:
    
                                                        change = False
    
                                                        #now we have a match(es)
                                                        #so update each record cautiously
                                                        if 'wof:coterminous' in props:
                                                            props['wof:coterminous'].append(int(p_id))
                                                            change = True
    
                                                        if 'wof:coterminous' in p_props:
                                                            p_props['wof:coterminous'].append(int(id))
                                                            change = True
    
                                                        if not 'wof:coterminous' in props:
                                                            props['wof:coterminous'] = [int(p_id)]
                                                            change = True
    
                                                        if not 'wof:coterminous' in p_props:
                                                            p_props['wof:coterminous'] = [int(id)]
                                                            change = True
    
                                                        #then sanitize for duplicates because some coterminous properties may already be set
                                                        #probably a much better way to do this...
                                                        coterm_ids = []
                                                        p_coterm_ids = []
    
                                                        for i in props['wof:coterminous']:
                                                            if not i in coterm_ids:
                                                                coterm_ids.append(i)
                                                        props['wof:coterminous'] = coterm_ids
    
                                                        for i in p_props['wof:coterminous']:
                                                            if not i in p_coterm_ids:
                                                                p_coterm_ids.append(i)
                                                        p_props['wof:coterminous'] = p_coterm_ids
    
                                                        #then write out
                                                        if change == True:

                                                            #but only write out if lists are not equal
                                                            #this will prevent exportifying records that already have coterminous set (and no changes occuring)
                                                            if not set(coterm) == set(props['wof:coterminous']):
                                                                exporter.export_feature(feature)

                                                            if not set(p_coterm) == set(p_props['wof:coterminous']):
                                                                exporter.export_feature(p_feature)
