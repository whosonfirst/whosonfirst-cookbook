# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import datetime
import os
import requests
import json
import mapzen.whosonfirst.utils
import mapzen.whosonfirst.export
import distance

if __name__ == "__main__":

    time1 = datetime.datetime.now()

    #alternatively, data could be set to a single pre-country repo or set of repos
    dir = os.getcwd()
    data = dir + "/data/"

    #set up crawl for each directory
    crawl = mapzen.whosonfirst.utils.crawl(data, inflate=True)
    exporter = mapzen.whosonfirst.export.flatfile(data)

    #needed to lookup correct 3 char lang codes
    lookup_table_langs = { "aa":"aar", "ab":"abk", "af":"afr", "ak":"aka", "am":"amh", "ar":"ara", "an":"arg", "as":"asm", "av":"ava", "ae":"ave", "ay":"aym", "az":"aze", "ba":"bak", "bm":"bam", "be":"bel", "bn":"ben", "bh":"bih", "bi":"bis", "bo":"bod", "bs":"bos", "br":"bre", "bg":"bul", "ca":"cat", "cs":"ces", "ch":"cha", "ce":"che", "cu":"chu", "cv":"chv", "kw":"cor", "co":"cos", "cr":"cre", "cy":"cym", "da":"dan", "de":"deu", "dv":"div", "dz":"dzo", "el":"ell", "en":"eng", "eo":"epo", "et":"est", "eu":"eus", "ee":"ewe", "fo":"fao", "fa":"fas", "fj":"fij", "fi":"fin", "fr":"fra", "fy":"fry", "ff":"ful", "gd":"gla", "ga":"gle", "gl":"glg", "gv":"glv", "gn":"grn", "gu":"guj", "ht":"hat", "ha":"hau", "he":"heb", "hz":"her", "hi":"hin", "ho":"hmo", "hr":"hrv", "hu":"hun", "hy":"hye", "ig":"ibo", "io":"ido", "ii":"iii", "iu":"iku", "ie":"ile", "ia":"ina", "id":"ind", "ik":"ipk", "is":"isl", "it":"ita", "jv":"jav", "ja":"jpn", "kl":"kal", "kn":"kan", "ks":"kas", "ka":"kat", "kr":"kau", "kk":"kaz", "km":"khm", "ki":"kik", "rw":"kin", "ky":"kir", "kv":"kom", "kg":"kon", "ko":"kor", "kj":"kua", "ku":"kur", "lo":"lao", "la":"lat", "lv":"lav", "li":"lim", "ln":"lin", "lt":"lit", "lb":"ltz", "lu":"lub", "lg":"lug", "mh":"mah", "ml":"mal", "mr":"mar", "mk":"mkd", "mg":"mlg", "mt":"mlt", "mn":"mon", "mi":"mri", "ms":"msa", "my":"mya", "na":"nau", "nv":"nav", "nr":"nbl", "nd":"nde", "ng":"ndo", "ne":"nep", "nl":"nld", "nn":"nno", "nb":"nob", "no":"nor", "ny":"nya", "oc":"oci", "oj":"oji", "or":"ori", "om":"orm", "os":"oss", "pa":"pan", "pi":"pli", "pl":"pol", "pt":"por", "ps":"pus", "qu":"que", "rm":"roh", "ro":"ron", "rn":"run", "ru":"rus", "sg":"sag", "sa":"san", "si":"sin", "sk":"slk", "sl":"slv", "se":"sme", "sm":"smo", "sn":"sna", "sd":"snd", "so":"som", "st":"sot", "es":"spa", "sq":"sqi", "sc":"srd", "sr":"srp", "ss":"ssw", "su":"sun", "sw":"swa", "sv":"swe", "ty":"tah", "ta":"tam", "tt":"tat", "te":"tel", "tg":"tgk", "tl":"tgl", "th":"tha", "ti":"tir", "to":"ton", "tn":"tsn", "ts":"tso", "tk":"tuk", "tr":"tur", "tw":"twi", "ug":"uig", "uk":"ukr", "ur":"urd", "uz":"uzb", "ve":"ven", "vi":"vie", "vo":"vol", "wa":"wln", "wo":"wol", "xh":"xho", "yi":"yid", "yo":"yor", "za":"zha", "zh":"zho", "zu":"zul", "zh-min-nan":"zh-min-nan"}

    #we'll use this as a counter for each new lang code added
    lang_counts_added = {}

    #set a list that we can use to append "highly populated" places to
    #this way, we can manually review changes to these places before merge
    manual_review = []

    count = 0

    for feature in crawl:

        name = ''
        import_lang_code = ''

        #we need to check how many names were added per record
        add_count = 0

        #append all api results to a new dict
        json_results = []

        will_pass = False

        props = feature['properties']

        #first, check if the record is current
        is_curr = -1
        if props.has_key('mz:is_current'):
            is_curr = props['mz:is_current']
        if not int(is_curr) == 0:

            update = False

            #first, if we have an existing wikidata concordance, use it
            if props.has_key('wof:concordances'):

                found_wd_id = False

                for k,v in props['wof:concordances'].items():
                    if k == 'wd:id':
                        wd_id = v
                        found_wd_id = True

                        try:
                            #using the found wd id, get the response
                            r = ("https://www.wikidata.org/w/api.php?action=wbgetentities&ids=%s&format=json" %wd_id)
                            result = requests.get(r)

                            #now convert the result to something usable
                            text_result = result.text
                            json_result = json.loads(text_result)
                            json_results.append(json_result)

                            #now grab the useful name/lang combos
                            wd_info = json_results[0]['entities'][wd_id]
                            wd_labels = wd_info['labels']

                            #now grab all language/value pairs from the response
                            for lang_set in wd_labels:
                                if len(wd_labels[lang_set]['language']) == 2:
                                    #by this point, we've got sets of language codes and names
                                    for k,v in lookup_table_langs.items():
                                        if wd_labels[lang_set]['language'] == k:
                                            import_lang_code = v
                                            name = wd_labels[lang_set]['value']

                                #sometimes we get a 3 char lang code, treat accordingly
                                if len(wd_labels[lang_set]['language']) == 3:
                                    import_lang_code = wd_labels[lang_set]['language']
                                    name = wd_labels[lang_set]['value']

                                #here, we're catching any strings that we've previously flagged as non-importable
                                flagged = False

                                #this probably needs work, but for now we'll strip out certain strings/chars from being added
                                for string in ['Timeline','Birthday','Aircraft','_',' de ',' n ',' do ',' di ',' i ','Political','Environmental','International','music','History','1','2','3','4','5','6','7','8','9','0']:
                                    if string in name:
                                        flagged = True

                                    #also flag when the name is one or two char in length
                                    if len(name) < 3:
                                        flagged = True

                                #also flag if admin place gets an airport code (campus check and ALL CAPS check)
                                if props['wof:placetype'] == 'campus':
                                    flagged = True

                                if name.isupper():
                                    flagged = True

                                if flagged == False:
                                    if not import_lang_code == "":
                                        if not name == "":
                                            #now we've got a name.. but sometimes it needs to be sanitized
                                            if ' (' in name:
                                                new_name = name.split(' (')
                                                name = new_name[0]

                                            if ', ' in name:
                                                new_name = name.split(', ')
                                                name = new_name[0]

                                            if '\xd8\x8c ' in name:
                                                new_name = name.split('\xd8\x8c ')
                                                name = new_name[0]

                                            #sometimes we get a funky country code appended to the name..
                                            if ' ' in name:
                                                name_split = name.split(' ')

                                                if len(name_split[-1]) == 1:
                                                    if name_split[-1].isupper():
                                                        name = name[:-2]

                                                if len(name_split[-1]) == 2:
                                                    if name_split[-1].isupper():
                                                        name = name[:-3]

                                                if len(name_split[-1]) == 3:
                                                    if name_split[-1].isupper():
                                                        name = name[:-4]

                                            #now check number of spaces in name and wof name
                                            to_update = False

                                            if not abs(int(props['wof:name'].count(' ')) - int(name.count(' '))) > 2:
                                                to_update = True

                                            if int(props['wof:name'].count(' ')) == 0:
                                                if abs(int(props['wof:name'].count(' ')) - int(name.count(' '))) > 1:
                                                    to_update = False

                                            #at this point, we've ditched adding names with "too many" words compared to default name
                                            if not name == '':
                                                if to_update:
                                                    #now that we've got a sanitized name, proceed with adding to name props
                                                    if props.has_key('name:' + str(import_lang_code) + '_x_preferred'):
                                                        #if we have a preferred name and variant already
                                                        if props.has_key('name:' + str(import_lang_code) + '_x_variant'):
                                                            if not name in props['name:' + str(import_lang_code) + '_x_variant']:
                                                                props['name:' + str(import_lang_code) + '_x_variant'].append(name)
                                                                update = True
                                                                add_count +=1

                                                        #if we have a preferred name but no variant
                                                        if not props.has_key('name:' + str(import_lang_code) + '_x_variant'):
                                                            props['name:' + str(import_lang_code) + '_x_variant'] = [name]
                                                            update = True
                                                            add_count +=1

                                                    #if there is no preferred
                                                    if not props.has_key('name:' + str(import_lang_code) + '_x_preferred'):
                                                        props['name:' + str(import_lang_code) + '_x_preferred'] = [name]
                                                        update = True
                                                        add_count +=1

                                                        #anytime we're adding a completely new language code (not appending)
                                                        #update the counter
                                                        if lang_counts_added.has_key(import_lang_code):
                                                            lang_counts_added[import_lang_code] = lang_counts_added[import_lang_code] + 1

                                                        if not lang_counts_added.has_key(import_lang_code):
                                                            lang_counts_added[import_lang_code] = 1

                                                    #now that we have added a name,
                                                    #do some sanitizing to ensure we're not duplicating values
                                                    if props.has_key('name:' + str(import_lang_code) + '_x_preferred'):
                                                        if props.has_key('name:' + str(import_lang_code) + '_x_variant'):
                                                            for item in props['name:' + str(import_lang_code) + '_x_variant']:
                                                                if item in props['name:' + str(import_lang_code) + '_x_preferred']:
                                                                    props['name:' + str(import_lang_code) + '_x_variant'].remove(item)
                                                                    update = True
                                                                    add_count -=1

                                                            if len(props['name:' + str(import_lang_code) + '_x_variant']) == 0:
                                                                del props['name:' + str(import_lang_code) + '_x_variant']
                                                                update = True

                        except:
                            print '\tFAILED: ' + str(props['wof:id'])

                #write out
                if update:
                    #while we may have flagged a record as "update", sometimes these additions are reverted
                    #this check ensures that we only export/update records that actually have a change at the end of all this work
                    if int(add_count) > 0:
                        if props.has_key('wof:population_rank'):
                            if int(props['wof:population_rank']) > 10:
                                manual_review.append(props['wof:id'])

                        #and finally, export the file
                        exporter.export_feature(feature)
                        count+=1

                #if we do not have a wikidata concordance, let's use the name
                #and gain names from the wikipedia response instead
                #
                #alternately, this if statement could be removed to append 
                #wikipedia names on top of the wikidata names
                if found_wd_id == False:
                    #here, we want to set the search name variable to the wof:name,
                    #unless we have an existing wk:page concordance
                    existing_name = props['wof:name']
                    if props.has_key('wof:concordances'):
                        for k,v in props['wof:concordances'].items():
                            if k == 'wk:page':
                                existing_name = v

                    #next, query the wikipedia API and parse response
                    #and again, try/except when calling the API...
                    try:
                        r = ("https://en.wikipedia.org/w/api.php?action=query&titles=%s&prop=langlinks&format=json" %existing_name)
                        result = requests.get(r)
                        text_result = result.text
                        json_result = json.loads(text_result)

                        #now, lets append this to a new list
                        #this is needed in case the response is split into many 'results'
                        json_results.append(json_result)

                        #now let's catch any more 'results'
                        while json_result!='null' and json_result.keys()[0]!='batchcomplete':
                            r = "https://en.wikipedia.org/w/api.php?action=query&titles=%s&prop=langlinks&format=json&llcontinue=%s" %(existing_name,json_result['continue']['llcontinue'])
                            result = requests.get(r)
                            text_result = result.text
                            json_result = json.loads(text_result)
                            json_results.append(json_result)

                        #now, let's check all results and iterate as needed
                        for i in json_results:
                            page = i['query']['pages']

                            for item in page:
                                for k,v in page[item].items():
                                    if k == 'langlinks':
                                        for translation_pairs in v:
                                            if len(translation_pairs['lang']) == 2:
                                                #by this point, we've got sets of language codes and names
                                                for k,v in lookup_table_langs.items():
                                                    if translation_pairs['lang'] == k:
                                                        import_lang_code = v
                                                        name = translation_pairs['*']

                                            #sometimes we get a 3 char lang code, treat accordingly
                                            if len(translation_pairs['lang']) == 3:
                                                import_lang_code = translation_pairs['lang']
                                                name = translation_pairs['*']

                                            #here, we're catching any strings that we've previously flagged as non-importable
                                            flagged = False

                                            #this probably needs work, but for now we'll strip out certain strings/chars from being added
                                            for string in ['Timeline','Birthday','Aircraft','_',' de ',' n ',' do ',' di ',' i ','Political','Environmental','International','music','History','1','2','3','4','5','6','7','8','9','0']:
                                                if string in name:
                                                    flagged = True

                                                #also flag when the name is one or two char in length
                                                if len(name) < 3:
                                                    flagged = True

                                            #also flag if admin place gets an airport code (campus check and ALL CAPS check)
                                            if props['wof:placetype'] == 'campus':
                                                flagged = True

                                            if name.isupper():
                                                flagged = True
        
                                            if flagged == False:
                                                if not import_lang_code == "":
                                                    if not name == "":
                                                        #now we've got a name.. but sometimes it needs to be sanitized
                                                        if ' (' in name:
                                                            new_name = name.split(' (')
                                                            name = new_name[0]

                                                        if ', ' in name:
                                                            new_name = name.split(', ')
                                                            name = new_name[0]

                                                        if '\xd8\x8c ' in name:
                                                            new_name = name.split('\xd8\x8c ')
                                                            name = new_name[0]

                                                        #sometimes we get a funky country code appended to the name..
                                                        if ' ' in name:
                                                            name_split = name.split(' ')

                                                            if len(name_split[-1]) == 1:
                                                                if name_split[-1].isupper():
                                                                    name = name[:-2]

                                                            if len(name_split[-1]) == 2:
                                                                if name_split[-1].isupper():
                                                                    name = name[:-3]

                                                            if len(name_split[-1]) == 3:
                                                                if name_split[-1].isupper():
                                                                    name = name[:-4]

                                                        #now check number of spaces in name and wof name
                                                        to_update = False

                                                        if not abs(int(props['wof:name'].count(' ')) - int(name.count(' '))) > 2:
                                                            to_update = True

                                                        if int(props['wof:name'].count(' ')) == 0:
                                                            if abs(int(props['wof:name'].count(' ')) - int(name.count(' '))) > 1:
                                                                to_update = False

                                                        #at this point, we've ditched adding names with "too many" words compared to default name
                                                        if not name == '':
                                                            if to_update:
                                                                #now that we've got a sanitized name, proceed with adding to name props
                                                                if props.has_key('name:' + str(import_lang_code) + '_x_preferred'):
                                                                    #if we have a preferred name and variant already
                                                                    if props.has_key('name:' + str(import_lang_code) + '_x_variant'):
                                                                        if not name in props['name:' + str(import_lang_code) + '_x_variant']:
                                                                            props['name:' + str(import_lang_code) + '_x_variant'].append(name)
                                                                            update = True
                                                                            add_count +=1

                                                                    #if we have a preferred name but no variant
                                                                    if not props.has_key('name:' + str(import_lang_code) + '_x_variant'):
                                                                        props['name:' + str(import_lang_code) + '_x_variant'] = [name]
                                                                        update = True
                                                                        add_count +=1

                                                                #if there is no preferred
                                                                if not props.has_key('name:' + str(import_lang_code) + '_x_preferred'):
                                                                    props['name:' + str(import_lang_code) + '_x_preferred'] = [name]
                                                                    update = True
                                                                    add_count +=1

                                                                    #anytime we're adding a completely new language code (not appending)
                                                                    #update the counter
                                                                    if lang_counts_added.has_key(import_lang_code):
                                                                        lang_counts_added[import_lang_code] = lang_counts_added[import_lang_code] + 1

                                                                    if not lang_counts_added.has_key(import_lang_code):
                                                                        lang_counts_added[import_lang_code] = 1

                                                                #now that we have added a name,
                                                                #do some sanitizing to ensure we're not duplicating values
                                                                if props.has_key('name:' + str(import_lang_code) + '_x_preferred'):
                                                                    if props.has_key('name:' + str(import_lang_code) + '_x_variant'):
                                                                        for item in props['name:' + str(import_lang_code) + '_x_variant']:
                                                                            if item in props['name:' + str(import_lang_code) + '_x_preferred']:
                                                                                props['name:' + str(import_lang_code) + '_x_variant'].remove(item)
                                                                                update = True
                                                                                add_count -=1

                                                                        if len(props['name:' + str(import_lang_code) + '_x_variant']) == 0:
                                                                            del props['name:' + str(import_lang_code) + '_x_variant']
                                                                            update = True

                    #print and append any failed id to a list for later use if failed
                    except:
                        print 'FAILED: ' + str(props['wof:id'])

                    #write out
                    if update:
                        #while we may have flagged a record as "update", sometimes these additions are reverted
                        #this check ensures that we only export/update records that actually have a change at the end of all this work
                        if int(add_count) > 0:
                            if props.has_key('wof:population_rank'):
                                if int(props['wof:population_rank']) > 10:
                                    manual_review.append(props['wof:id'])

                            #and finally, export the file
                            exporter.export_feature(feature)
                            count+=1

    #optional, this simply outputs some metrics
    total = 0
    for k,v in sorted(lang_counts_added.items()):
        print k,v
        total+=v
    print 'total names added: ' + str(total)
    print '\r'
    #output ids that need to be reviewed
    for id in manual_review:
        print id
    print '\r'
    print 'total updated features: ' + str(count)
    print '\r'
    time2 = datetime.datetime.now()
    print str(time1) + '  to  ' + str(time2)