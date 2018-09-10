#import all the packages we need
import sys
import os
import logging
import optparse
import csv
import json
import re

reload(sys)  
sys.setdefaultencoding('utf8')

import geojson
import pprint
import requests
import mapzen.whosonfirst.utils
import mapzen.whosonfirst.placetypes
import mapzen.whosonfirst.export
import mapzen.whosonfirst.api.client

logging.basicConfig(level=logging.INFO)

#setup command line option parsers
if __name__ == '__main__':

    opt_parser = optparse.OptionParser()

    opt_parser.add_option('-i', '--input', dest='input', action='store', default=None, help='Where to read CSV import file from')
    opt_parser.add_option('-m', '--meta', dest='meta', action='store', default=None, help='Where to read meta file from')
    opt_parser.add_option('-o', '--output', dest='output', action='store', default="/path/to/whosonfirst-data/data", help='Where to write WOF records to')
    opt_parser.add_option('-d', '--denominator', dest='denominator', type="int", action='store', default=1)
    opt_parser.add_option('-v', '--verbose', dest='verbose', action='store_true')

    options, args = opt_parser.parse_args()

    # CSV file to process
    places = options.input
    fh = open(places, 'r')
    
    places_meta = options.meta
    fh_meta = open(places_meta, 'r')
    
    # where to put the results
    source = os.path.abspath(options.output)
    exporter = mapzen.whosonfirst.export.flatfile(source)

    # start processing the records to deprecate
    #csv.reader(data.splitlines(), delimiter='\t')
    reader_geonames_name_alts = csv.DictReader(fh, dialect=csv.excel_tab)
    reader_wof_metafile = csv.DictReader(fh_meta)

    lookup_table_langs = { "aa":"aar", "ab":"abk", "af":"afr", "ak":"aka", "am":"amh", "ar":"ara", "an":"arg", "as":"asm", "av":"ava", "ae":"ave", "ay":"aym", "az":"aze", "ba":"bak", "bm":"bam", "be":"bel", "bn":"ben", "bh":"bih", "bi":"bis", "bo":"bod", "bs":"bos", "br":"bre", "bg":"bul", "ca":"cat", "cs":"ces", "ch":"cha", "ce":"che", "cu":"chu", "cv":"chv", "kw":"cor", "co":"cos", "cr":"cre", "cy":"cym", "da":"dan", "de":"deu", "dv":"div", "dz":"dzo", "el":"ell", "en":"eng", "eo":"epo", "et":"est", "eu":"eus", "ee":"ewe", "fo":"fao", "fa":"fas", "fj":"fij", "fi":"fin", "fr":"fra", "fy":"fry", "ff":"ful", "gd":"gla", "ga":"gle", "gl":"glg", "gv":"glv", "gn":"grn", "gu":"guj", "ht":"hat", "ha":"hau", "he":"heb", "hz":"her", "hi":"hin", "ho":"hmo", "hr":"hrv", "hu":"hun", "hy":"hye", "ig":"ibo", "io":"ido", "ii":"iii", "iu":"iku", "ie":"ile", "ia":"ina", "id":"ind", "ik":"ipk", "is":"isl", "it":"ita", "jv":"jav", "ja":"jpn", "kl":"kal", "kn":"kan", "ks":"kas", "ka":"kat", "kr":"kau", "kk":"kaz", "km":"khm", "ki":"kik", "rw":"kin", "ky":"kir", "kv":"kom", "kg":"kon", "ko":"kor", "kj":"kua", "ku":"kur", "lo":"lao", "la":"lat", "lv":"lav", "li":"lim", "ln":"lin", "lt":"lit", "lb":"ltz", "lu":"lub", "lg":"lug", "mh":"mah", "ml":"mal", "mr":"mar", "mk":"mkd", "mg":"mlg", "mt":"mlt", "mn":"mon", "mi":"mri", "ms":"msa", "my":"mya", "na":"nau", "nv":"nav", "nr":"nbl", "nd":"nde", "ng":"ndo", "ne":"nep", "nl":"nld", "nn":"nno", "nb":"nob", "no":"nor", "ny":"nya", "oc":"oci", "oj":"oji", "or":"ori", "om":"orm", "os":"oss", "pa":"pan", "pi":"pli", "pl":"pol", "pt":"por", "ps":"pus", "qu":"que", "rm":"roh", "ro":"ron", "rn":"run", "ru":"rus", "sg":"sag", "sa":"san", "si":"sin", "sk":"slk", "sl":"slv", "se":"sme", "sm":"smo", "sn":"sna", "sd":"snd", "so":"som", "st":"sot", "es":"spa", "sq":"sqi", "sc":"srd", "sr":"srp", "ss":"ssw", "su":"sun", "sw":"swa", "sv":"swe", "ty":"tah", "ta":"tam", "tt":"tat", "te":"tel", "tg":"tgk", "tl":"tgl", "th":"tha", "ti":"tir", "to":"ton", "tn":"tsn", "ts":"tso", "tk":"tuk", "tr":"tur", "tw":"twi", "ug":"uig", "uk":"ukr", "ur":"urd", "uz":"uzb", "ve":"ven", "vi":"vie", "vo":"vol", "wa":"wln", "wo":"wol", "xh":"xho", "yi":"yid", "yo":"yor", "za":"zha", "zh":"zho", "zu":"zul" }

#     name in reader_geonames_name_alts:

#         #alternateNameId   : the id of this alternate_name, int
#         #geonameid         : geonameId referring to id in table 'geoname', int
#         #isolanguage       : iso 639 language code 2- or 3-characters; 4-characters 'post' for postal codes and 'iata','icao' and faac for airport codes, fr_1793 for French Revolution names,  abbr for abbreviation, link for a website, varchar(7)
#         #alternate_name    : alternate_name or name variant, varchar(400)
#         #isPreferredName   : '1', if this alternate_name is an official/preferred name
#         #isShortName       : '1', if this is a short name like 'California' for 'State of California'
#         #isColloquial      : '1', if this alternate_name is a colloquial or slang term
#         #isHistoric        : '1', if this alternate_name is historic and was used in the past

#         alternateNameId = name['alternateNameId']
#         geonameid       = name['geonameid']
#         isolanguage     = name['isolanguage']
#         alternate_name  = name['alternate_name']
#         isPreferredName = name['isPreferredName']
#         isShortName     = name['isShortName']
#         isColloquial    = name['isColloquial']
#         isHistoric      = name['isHistoric']

    counter = 0
    gn_wof_id_lookup = {}
    
    for row in reader_wof_metafile:
        if row["gn:id"]:
            gn_wof_id_lookup[ "a_" + row["gn:id"] ] = row["wof:id"]

    # now loop over the geonames 
    for gn_name in reader_geonames_name_alts:
        counter+=1

        # only print out after a while
        if counter % options.denominator == 0:
            print "\n\t"+str(counter)+"\n"

        # do we have a concordance between WOF and GN?
        gn_id = "a_" + gn_name["geonameid"]
        if gn_wof_id_lookup.has_key( gn_id ):
            feature = mapzen.whosonfirst.utils.load( source, gn_wof_id_lookup[ gn_id ] )

            if feature:
                props = feature['properties']

                #check to see if the record has been superseded..
                #if it has, load the feature that comes after it...
                if props.has_key('wof:superseded_by'):
                    if len(props['wof:superseded_by']) == 1:
                        id = int(props['wof:superseded_by'][0])
                        feature = mapzen.whosonfirst.utils.load(source, id)
                        if feature:
                            props = feature['properties']

                # for this name, it doesn't have a language code until we figure it out
                lang_code_3_char = None
            
                #we need to validate (or create) a three character lang code variable...
                len_lc = len(gn_name['isolanguage'])
                if len_lc == 2:
                    lang_code_3_char = lookup_table_langs[ str(gn_name['isolanguage']) ]
                elif len_lc == 3:
                    lang_code_3_char = gn_name['isolanguage']
                # there are a lot of unknown language codes (not a 1% case)
                elif len_lc == 0:
                    lang_code_3_char = 'unk'

                #if we have an abbreviation, set it as the abbreviation:eng_x_preferred..
                #abbr is the only valid four digit isoLang code to import, let's capture it here
                #and not assign it to other props
                #
                if gn_name['isolanguage'] == 'abbr':
                    if props.has_key('abbreviation:eng_x_preferred'):
                        if unicode(gn_name['alternate_name']) not in props['abbreviation:eng_x_preferred']:
                            if props.has_key('abbreviation:eng_x_variant'):
                                if unicode(gn_name['alternate_name']) not in props['abbreviation:eng_x_variant']:
                                    props['abbreviation:eng_x_preferred'].append(gn_name['alternate_name'])
                                    exporter.export_feature(feature)
                    else:
                        props['abbreviation:eng_x_preferred'] = [gn_name['alternate_name']]
                        exporter.export_feature(feature)
                
                    # we have a few of these in WOF already, leave them alone if present
                    if not props.has_key('wof:abbreviation'):
                        # note, this property isn't a list
                        props['wof:abbreviation'] = gn_name['alternate_name']
                        exporter.export_feature(feature)

                #if we DO have a lang code variable...
                elif lang_code_3_char:
                    #set preferred name
                    if gn_name.has_key('isPreferredName'):
                        if gn_name['isPreferredName'] == '1' and lang_code_3_char != 'unk':
                            if props.has_key('name:'+lang_code_3_char+'_x_preferred'):
                                if props.has_key('name:'+lang_code_3_char+'_x_variant'):
                                    if unicode(gn_name['alternate_name']) not in props['name:'+lang_code_3_char+'_x_variant']:
                                        if unicode(gn_name['alternate_name']) not in props['name:'+lang_code_3_char+'_x_preferred']:
                                            props['name:'+lang_code_3_char+'_x_variant'].append(gn_name['alternate_name'])
                                            exporter.export_feature(feature)
                            else:
                                props['name:'+lang_code_3_char+'_x_preferred'] = [gn_name['alternate_name']]
                                exporter.export_feature(feature)

                    #set colloquial name
                    if gn_name.has_key('isColloquial'):
                        if gn_name['isColloquial'] == '1' and lang_code_3_char != 'unk':
                            if props.has_key('name:'+lang_code_3_char+'_x_colloquial'):
                                if gn_name['alternate_name'] not in props['name:'+lang_code_3_char+'_x_colloquial']:
                                    props['name:'+lang_code_3_char+'_x_colloquial'].append(gn_name['alternate_name'])
                                    exporter.export_feature(feature)
                            else:
                                props['name:'+lang_code_3_char+'_x_colloquial'] = [gn_name['alternate_name']]
                                exporter.export_feature(feature)

                    #set historic name
                    if gn_name.has_key('isHistoric'):
                        if gn_name['isHistoric'] == '1' and lang_code_3_char != 'unk':
                            if props.has_key('name:'+lang_code_3_char+'_x_historical'):
                                if gn_name['alternate_name'] not in props['name:'+lang_code_3_char+'_x_historical']:
                                    props['name:'+lang_code_3_char+'_x_historical'].append(gn_name['alternate_name'])
                                    exporter.export_feature(feature)
                            else:
                                props['name:'+lang_code_3_char+'_x_historical'] = [gn_name['alternate_name']]
                                exporter.export_feature(feature)

                    #set VARIANT abbr name
                    if gn_name.has_key('isShortName'):
                        if gn_name['isShortName'] == '1' and lang_code_3_char != 'unk':
                            if props.has_key('name:'+lang_code_3_char+'_x_variant'):
                                if unicode(gn_name['alternate_name']) not in props['name:'+lang_code_3_char+'_x_variant']:
                                    if props.has_key('name:'+lang_code_3_char+'_x_preferred'):
                                        if unicode(gn_name['alternate_name']) not in props['name:'+lang_code_3_char+'_x_preferred']:
                                            props['name:'+lang_code_3_char+'_x_variant'].append(gn_name['alternate_name'])
                                            exporter.export_feature(feature)
                            else:
                                if props.has_key('name:'+lang_code_3_char+'_x_preferred'):
                                    if unicode(gn_name['alternate_name']) not in props['name:'+lang_code_3_char+'_x_preferred']:
                                        props['name:'+lang_code_3_char+'_x_variant'] = [gn_name['alternate_name']]
                                        exporter.export_feature(feature)

                    #otherwise...
                    else:
                        if props.has_key('name:'+lang_code_3_char+'_x_variant'):
                            if unicode(gn_name['alternate_name']) not in props['name:'+lang_code_3_char+'_x_variant']:
                                if props.has_key('name:'+lang_code_3_char+'_x_preferred'):
                                    if unicode(gn_name['alternate_name']) not in props['name:'+lang_code_3_char+'_x_preferred']:
                                        props['name:'+lang_code_3_char+'_x_variant'].append(gn_name['alternate_name'])
                                        exporter.export_feature(feature)
                        else:
                            if props.has_key('name:'+lang_code_3_char+'_x_preferred'):
                                if unicode(gn_name['alternate_name']) not in props['name:'+lang_code_3_char+'_x_preferred']:
                                    props['name:'+lang_code_3_char+'_x_variant'] = [gn_name['alternate_name']]
                                    exporter.export_feature(feature)
                            else:
                                if lang_code_3_char != 'unk':
                                    props['name:'+lang_code_3_char+'_x_preferred'] = [gn_name['alternate_name']]
                                    exporter.export_feature(feature)

                                else:
                                    # assume we should add until provin guilty
                                    # special handling for wof:name, really name:unk_x_... are variants of that (because English ASCII7)
                                    # special handling for English and Russian as most of the unknown seem to be in one of those languages
                                    should_add = True
                                    if props.has_key('wof:name'):
                                        if unicode(gn_name['alternate_name']) == props['wof:name']:
                                            should_add = False
                                    elif props.has_key('name:eng_x_preferred'):
                                        if unicode(gn_name['alternate_name']) in props['name:eng_x_preferred']:
                                            should_add = False
                                    elif props.has_key('name:eng_x_variant'):
                                        if unicode(gn_name['alternate_name']) in props['name:eng_x_variant']:
                                            should_add = False
                                    elif props.has_key('name:rus_x_preferred'):
                                        if unicode(gn_name['alternate_name']) in props['name:rus_x_preferred']:
                                            should_add = False
                                    elif props.has_key('name:rus_x_variant'):
                                        if unicode(gn_name['alternate_name']) in props['name:rus_x_variant']:
                                            should_add = False

                                    if should_add:
                                        props['name:'+lang_code_3_char+'_x_variant'] = [gn_name['alternate_name']]
                                        exporter.export_feature(feature)

                if options.verbose:
                    print str(props['wof:id'])
                    #print str(props['wof:id']) + ' is done for GN ' + str(gn_name["geonameid"]) + " for " + [gn_name['alternate_name']                    print str(props['wof:id']) + ' is done for GN ' + str(gn_name["geonameid"]) + " for " + [gn_name['alternate_name']
