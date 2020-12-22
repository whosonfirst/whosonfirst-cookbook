#stepps00 - 2020.04.14
#this script titlecases the locality name
#and adds all locality names plus the amount of times the locality name occurs

import sys
import os
import logging
import optparse
import csv
import pprint
import datetime
import mapzen.whosonfirst.utils
import mapzen.whosonfirst.placetypes
import mapzen.whosonfirst.export
import json
import geojson
import operator

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':

    opt_parser = optparse.OptionParser()
    opt_parser.add_option('-i', '--input', dest='input', action='store', default=None, help='Where to read CSV import file from')
    options, args = opt_parser.parse_args()

    places = options.input
    fh = open(places, 'r')
    reader = csv.DictReader(fh)

    #mapping of all states <> zip prefixes
    #minus DC and NY because those are special cases
    state_starting_codes = {'Alabama':'35','Alabama':'36','Alaska':'995','Alaska':'996','Alaska':'997','Alaska':'998','Alaska':'999','Arizona':'85','Arizona':'86','Arkansas':'716','Arkansas':'717','Arkansas':'718','Arkansas':'719','Arkansas':'720','Arkansas':'721','Arkansas':'722','Arkansas':'723','Arkansas':'724','Arkansas':'725','Arkansas':'726','Arkansas':'727','Arkansas':'728','Arkansas':'729','California':'900','California':'901','California':'902','California':'903','California':'904','California':'905','California':'906','California':'907','California':'908','California':'909','California':'910','California':'911','California':'912','California':'913','California':'914','California':'915','California':'916','California':'917','California':'918','California':'919','California':'920','California':'921','California':'922','California':'923','California':'924','California':'925','California':'926','California':'927','California':'928','California':'929','California':'930','California':'931','California':'932','California':'933','California':'934','California':'935','California':'936','California':'937','California':'938','California':'939','California':'940','California':'941','California':'942','California':'943','California':'944','California':'945','California':'946','California':'947','California':'948','California':'949','California':'950','California':'951','California':'952','California':'953','California':'954','California':'955','California':'956','California':'957','California':'958','California':'959','California':'960','California':'961','Colorado':'80','Colorado':'81','Connecticut':'06','Delaware':'197','Delaware':'198','Delaware':'199','Florida':'32','Florida':'33','Florida':'34','Georgia':'30','Georgia':'31','Geogria':'398','Geogria':'399','Hawaii':'967','Hawaii':'968','Idaho':'832','Idaho':'833','Idaho':'834','Idaho':'835','Idaho':'836','Idaho':'837','Idaho':'838','Idaho':'839','Illinois':'60','Illinois':'61','Illinois':'62','Indiana':'46','Indiana':'47','Iowa':'50','Iowa':'51','Iowa':'52','Kansas':'66','Kansas':'67','Kentucky':'40','Kentucky':'41','Kentucky':'42','Louisiana':'700','Louisiana':'701','Louisiana':'702','Louisiana':'703','Louisiana':'704','Louisiana':'705','Louisiana':'706','Louisiana':'707','Louisiana':'708','Louisiana':'709','Louisiana':'710','Louisiana':'711','Louisiana':'712','Louisiana':'713','Louisiana':'714','Louisiana':'715','Maine':'039','Maine':'040','Maine':'041','Maine':'042','Maine':'043','Maine':'044','Maine':'045','Maine':'046','Maine':'047','Maine':'048','Maine':'049','Maryland':'206','Maryland':'207','Maryland':'208','Maryland':'209','Maryland':'210','Maryland':'211','Maryland':'212','Maryland':'213','Maryland':'214','Maryland':'215','Maryland':'216','Maryland':'217','Maryland':'218','Maryland':'219','Massachusetts':'010','Massachusetts':'011','Massachusetts':'012','Massachusetts':'013','Massachusetts':'014','Massachusetts':'015','Massachusetts':'016','Massachusetts':'017','Massachusetts':'018','Massachusetts':'019','Massachusetts':'020','Massachusetts':'021','Massachusetts':'022','Massachusetts':'023','Massachusetts':'024','Massachusetts':'025','Massachusetts':'026','Massachusetts':'027','Michigan':'48','Michigan':'49','Minnesota':'550','Minnesota':'551','Minnesota':'552','Minnesota':'553','Minnesota':'554','Minnesota':'555','Minnesota':'556','Minnesota':'557','Minnesota':'558','Minnesota':'559','Minnesota':'560','Minnesota':'561','Minnesota':'562','Minnesota':'563','Minnesota':'564','Minnesota':'565','Minnesota':'566','Minnesota':'567','Mississippi':'386','Mississippi':'387','Mississippi':'388','Mississippi':'389','Mississippi':'390','Mississippi':'391','Mississippi':'392','Mississippi':'393','Mississippi':'394','Mississippi':'395','Mississippi':'396','Mississippi':'397','Missouri':'63','Missouri':'64','Missouri':'65','Montana':'59','Nebraska':'68','Nebraska':'69','Nevada':'889','Nevada':'890','Nevada':'891','Nevada':'892','Nevada':'893','Nevada':'894','Nevada':'895','Nevada':'896','Nevada':'897','Nevada':'898','Nevada':'899','New Hampshire':'030','New Hampshire':'031','New Hampshire':'032','New Hampshire':'033','New Hampshire':'034','New Hampshire':'035','New Hampshire':'036','New Hampshire':'037','New Hampshire':'038','New Jersey':'07','New Jersey':'08','New Mexico':'870','New Mexico':'871','New Mexico':'872','New Mexico':'873','New Mexico':'874','New Mexico':'875','New Mexico':'876','New Mexico':'877','New Mexico':'878','New Mexico':'879','New Mexico':'880','New Mexico':'881','New Mexico':'882','New Mexico':'883','New Mexico':'884','North Carolina':'27','North Carolina':'28','North Dakota':'58','Ohio':'43','Ohio':'44','Ohio':'45','Oklahoma':'73','Oklahoma':'74','Oregon':'97','Pennsylvania':'150','Pennsylvania':'151','Pennsylvania':'152','Pennsylvania':'153','Pennsylvania':'154','Pennsylvania':'155','Pennsylvania':'156','Pennsylvania':'157','Pennsylvania':'158','Pennsylvania':'159','Pennsylvania':'160','Pennsylvania':'161','Pennsylvania':'162','Pennsylvania':'163','Pennsylvania':'164','Pennsylvania':'165','Pennsylvania':'166','Pennsylvania':'167','Pennsylvania':'168','Pennsylvania':'169','Pennsylvania':'170','Pennsylvania':'171','Pennsylvania':'172','Pennsylvania':'173','Pennsylvania':'174','Pennsylvania':'175','Pennsylvania':'176','Pennsylvania':'177','Pennsylvania':'178','Pennsylvania':'179','Pennsylvania':'180','Pennsylvania':'181','Pennsylvania':'182','Pennsylvania':'183','Pennsylvania':'184','Pennsylvania':'185','Pennsylvania':'186','Pennsylvania':'187','Pennsylvania':'188','Pennsylvania':'189','Pennsylvania':'190','Pennsylvania':'191','Pennsylvania':'192','Pennsylvania':'193','Pennsylvania':'194','Pennsylvania':'195','Pennsylvania':'196','Rhode Island':'028','Rhode Island':'029','South Carolina':'29','South Dakota':'57','Tennessee':'370','Tennessee':'371','Tennessee':'372','Tennessee':'373','Tennessee':'374','Tennessee':'375','Tennessee':'376','Tennessee':'377','Tennessee':'378','Tennessee':'379','Tennessee':'380','Tennessee':'381','Tennessee':'382','Tennessee':'383','Tennessee':'384','Tennessee':'385','Texas':'75','Texas':'76','Texas':'77','Texas':'78','Texas':'79','Utah':'84','Vermont':'05','Virginia':'201','Virginia':'220','Virginia':'221','Virginia':'222','Virginia':'223','Virginia':'224','Virginia':'225','Virginia':'226','Virginia':'227','Virginia':'228','Virginia':'229','Virginia':'230','Virginia':'231','Virginia':'232','Virginia':'233','Virginia':'234','Virginia':'235','Virginia':'236','Virginia':'237','Virginia':'238','Virginia':'239','Virginia':'240','Virginia':'241','Virginia':'242','Virginia':'243','Virginia':'244','Virginia':'245','Virginia':'246','Washington':'980','Washington':'981','Washington':'982','Washington':'983','Washington':'984','Washington':'985','Washington':'986','Washington':'987','Washington':'988','Washington':'989','Washington':'990','Washington':'991','Washington':'992','Washington':'993','Washington':'994','West Virginia':'247','West Virginia':'248','West Virginia':'249','West Virginia':'250','West Virginia':'251','West Virginia':'252','West Virginia':'253','West Virginia':'254','West Virginia':'255','West Virginia':'256','West Virginia':'257','West Virginia':'258','West Virginia':'259','West Virginia':'260','West Virginia':'261','West Virginia':'262','West Virginia':'263','West Virginia':'264','West Virginia':'265','West Virginia':'266','West Virginia':'267','West Virginia':'268','West Virginia':'269','Wisconsin':'53','Wisconsin':'54','Wyoming':'820','Wyoming':'821','Wyoming':'822','Wyoming':'823','Wyoming':'824','Wyoming':'825','Wyoming':'826','Wyoming':'827','Wyoming':'828','Wyoming':'829','Wyoming':'830','Wyoming':'831'}

    #will use this to append locality names <> postalcode matches
    mapping = {}

    #used later to check for bunk locality names
    numbers = [0,1,2,3,4,5,6,7,8,9]

    counter = 0

    for row in reader:
        _locality = row['locality']
        _postal_code = row['postal_code']
        _locality = _locality.title()

        #.title() is great, but sometimes needs adjustments
        if "'S " in _locality:
            _locality.replace("'S ", "'s ")
        if " Of " in _locality:
            _locality.replace(" Of ", " of ")

        id = row['id']

        #assume importable, unless we flag later on
        okay = True

        #debugging in terminal
        counter+=1
        if counter % 10000 == 0:
            print counter 

        #remove bunk chars
        if not _postal_code in [' ',None,'null','NULL','N/A','','.',',']:
            if not _locality in [' ',None,'null','NULL','N/A','','.',',']:
                #and completely ditch if the locality name has a number
                for num in numbers:
                    if str(num) in _locality:
                       okay = False
                       
                #split on dash in US
                if '-' in _postal_code:
                    new_postal_code = _postal_code.split('-')
                    _postal_code = new_postal_code[0]
    
                #remove over five chars
                if len(_postal_code) > 5:
                    _postal_code = _postal_code[:5]

                #for the US, drop any postalcodes shorter than five char
                if not len(_postal_code) < 5:
                    for item in state_starting_codes:
                        if _postal_code.startswith(item):
                            if _locality == state_starting_codes[item]:
                                okay = False

                    #if we still have an okay match...
                    if okay == True:
                        #order of operations to check if we need to append counts or create new var mapping
                        if mapping.has_key(_postal_code):
                            if mapping[_postal_code].has_key(_locality):
                                mapping[_postal_code][_locality]+=1
    
                            if not mapping[_postal_code].has_key(_locality):
                                mapping[_postal_code][_locality] = 1
        
                        if not mapping.has_key(_postal_code):
                            mapping[_postal_code] = {_locality:1}

    #set this up to scrub the first mapping dict
    new_mapping = {}

    for item in mapping:
        #sort each zip by ranked names
        i = mapping[item]
        sorted_item = sorted(i.items(), key=lambda t: t[1], reverse=True)

        #then remove single values
        new_mapping[item] = sorted_item

    #output matching postalcodes and scrubbed locality names
    for item in new_mapping:

        caught = False
        pref_name = ''
        var_names = []

        #for every name/occurrence # pair...
        for key, value in new_mapping[item]:
            #if the locality name if found 5 or more times, use it
            if not int(value) < 5:
                if caught == True:
                    var_names.append(key)
                if caught == False:
                    pref_name = key
                    caught = True

        var_list = ':'.join(var_names)

        #output
        print '"' + str(item) + '"' + '\t' + '"' + str(pref_name) + '"' + '\t' + '"' + str(var_list) + '"'
