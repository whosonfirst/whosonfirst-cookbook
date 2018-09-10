import sys
import os
import logging
import datetime
import optparse
import csv
import json
import geojson
import requests

import pprint
import mapzen.whosonfirst.utils
import mapzen.whosonfirst.placetypes
import mapzen.whosonfirst.export

if __name__ == '__main__':

    opt_parser = optparse.OptionParser()
    opt_parser.add_option('-i', '--input', dest='input', action='store', default=None, help='Where to read CSV import file from')
    opt_parser.add_option('-o', '--output', dest='output', action='store', default="/path/to/whosonfirst-data/data", help='Where to write WOF records to')

    options, args = opt_parser.parse_args()
    places = options.input
    fh = open(places, 'r')
    source = os.path.abspath(options.output)
    exporter = mapzen.whosonfirst.export.flatfile(source)
    reader = csv.DictReader(fh)

    #lookup chart for country code
    country_code_id_lookup = {
        "NL" : 136251281,
        "GU" : 85632163,
        "VI" : 85632169,
        "MP" : 85632421,
        "BL" : 85632199,
        "KY" : 85632611,
        "XY" : -1,
        "XY" : -1,
        "TC" : 85632205,
        "VG" : 85632629,
        "UM" : 85632333,
        "TF" : 1108833329, ####
        "IO" : 85632641,
        "FK" : 85632211,
        "BM" : 85632731,
        "IO" : 85632459,
        "XX" : -1,
        "PF" : 85632653,
        "NF" : 85632517,
        "XY" : -1,
        "XY" : -1,
        "FO" : 85633153,
        "GI" : 85633167,
        "NC" : 85632473,
        "HM" : 85632239,
        "MS" : 85632677,
        "CK" : 85632481,
        "SH" : 85632485,
        "NU" : 85632493,
        "CX" : 874411115, ####
        "PR" : 85633729,
        "TF" : 85632549,
        "AX" : 85632789,
        "WF" : 85632585,
        "PN" : 85632587,
        "AI" : 85632283,
        "XY" : -1,
        "AS" : 85632697,
        "GS" : 85632301,
        "BH" : 85632167,
        "BT" : 85632171,
        "LS" : 85632173,
        "PA" : 85632179,
        "RW" : 85632303,
        "MV" : 85632305,
        "TW" : 85632403,
        "AL" : 85632405,
        "MM" : 85632181,
        "SX" : 85632185,
        "VA" : 85632187,
        "GA" : 85632407,
        "GH" : 85632189,
        "SY" : 85632413,
        "GP" : 85671209, ####
        "IQ" : 85632191,
        "JO" : 85632425,
        "DM" : 85632503,
        "KZ" : 85632307,
        "LK" : 85632313,
        "IL" : 85632315,
        "GM" : 85632603,
        "SG" : 85632605,
        "TV" : 85632607,
        "BA" : 85632609,
        "BO" : 85632623,
        "VE" : 85632317,
        "JP" : 85632429,
        "DJ" : 85632319,
        "TN" : 85632703,
        "FM" : 85632431,
        "KI" : 85632709,
        "AR" : 85632505,
        "HN" : 85632323,
        "UG" : 85632625,
        "DO" : 85632713,
        "ID" : 85632203,
        "HT" : 85632433,
        "LY" : 85632627,
        "TD" : 85632325,
        "SZ" : 85632635,
        "CY" : 85632437,
        "OM" : 85632207,
        "KE" : 85632329,
        "PW" : 85632331,
        "MN" : 85632439,
        "GD" : 85632335,
        "CW" : 85632441,
        "AQ" : 85632715,
        "AZ" : 85632717,
        "CV" : 85632721,
        "AN" : 136251281, ####
        "SR" : 85632443,
        "KP" : 85632639,
        "BF" : 85632213,
        "JM" : 85632215,
        "EH" : 85632217,
        "MG" : 85632223,
        "CI" : 85632449,
        "BS" : 85632339,
        "AD" : 85632343,
        "PG" : 85632347,
        "RE" : 85671199, ####
        "PY" : 85632355,
        "MZ" : 85632729,
        "XS" : -1,
        "MU" : 85632357,
        "CD" : 85632643,
        "TZ" : 85632227,
        "DZ" : 85632451,
        "KH" : 85632359,
        "UZ" : 85632645,
        "TO" : 85632455,
        "IM" : 85632461,
        "PH" : 85632509,
        "NG" : 85632735,
        "TG" : 85632647,
        "NP" : 85632465,
        "BR" : 85633009,
        "UY" : 85632511,
        "SL" : 85632467,
        "AF" : 85632229,
        "TJ" : 85632513,
        "IR" : 85632361,
        "MY" : 85632739,
        "NR" : 85632747,
        "BN" : 85632749,
        "SS" : 85632657,
        "SN" : 85632365,
        "LC" : 85632369,
        "PM" : 85632371,
        "CO" : 85632519,
        "PK" : 85632659,
        "MK" : 85632373,
        "SC" : 85632661,
        "SO" : 85632379,
        "SD" : 85632751,
        "MH" : 85632663,
        "DE" : 85633111,
        "DK" : 85633121,
        "ME" : 85632667,
        "TM" : 85632671,
        "MW" : 85632383,
        "ES" : 85633129,
        "EE" : 85633135,
        "KR" : 85632231,
        "FI" : 85633143,
        "GT" : 85632385,
        "GF" : 85671195, ####
        "FR" : 85633147,
        "CH" : 85633051,
        "IN" : 85632469,
        "GB" : 85633159,
        "GE" : 85633163,
        "FJ" : 85632755,
        "GR" : 85633171,
        "PE" : 85632521,
        "YT" : 85671203, ####
        "AG" : 85632529,
        "MQ" : 85671191, ####
        "CF" : 85632391,
        "GW" : 85632757,
        "LB" : 85632533,
        "BW" : 85632235,
        "HR" : 85633229,
        "HU" : 85633237,
        "NA" : 85632535,
        "IE" : 85633241,
        "IS" : 85633249,
        "IT" : 85633253,
        "CU" : 85632675,
        "XK" : 85633259,
        "LI" : 85633267,
        "LT" : 85633269,
        "MR" : 85632679,
        "WS" : 85632681,
        "BD" : 85632475,
        "KG" : 85632761,
        "LA" : 85632241,
        "HK" : 85632483,
        "LU" : 85633275,
        "LV" : 85633279,
        "MC" : 85633285,
        "MD" : 85633287,
        "TR" : 85632393,
        "CR" : 85632487,
        "BB" : 85632491,
        "CG" : 85632541,
        "MX" : 85633293,
        "CC" : 85632495,
        "ZW" : 85632243,
        "CM" : 85632245,
        "YE" : 85632499,
        "NL" : 85633337,
        "SV" : 85632545,
        "GG" : 85632547,
        "KN" : 85632551,
        "PT" : 85633735,
        "BJ" : 85632247,
        "BY" : 85632395,
        "NO" : 85633341,
        "ML" : 85632553,
        "PS" : 85633739,
        "LR" : 85632249,
        "SA" : 85632253,
        "GY" : 85632397,
        "RO" : 85633745,
        "ZA" : 85633813,
        "RS" : 85633755,
        "SM" : 85633763,
        "SK" : 85633769,
        "SI" : 85633779,
        "ZM" : 85632559,
        "SE" : 85633789,
        "VC" : 85632569,
        "ET" : 85632257,
        "KM" : 85632259,
        "BZ" : 85632571,
        "VN" : 85632763,
        "ST" : 85632765,
        "AE" : 85632573,
        "EC" : 85632261,
        "AM" : 85632773,
        "VU" : 85632263,
        "ER" : 85632781,
        "AT" : 85632785,
        "NE" : 85632269,
        "TT" : 85632271,
        "EG" : 85632581,
        "TL" : 85632583,
        "AO" : 85632281,
        "BI" : 85632285,
        "GQ" : 85632287,
        "US" : 85633793,
        "SB" : 85632591,
        "JE" : 85632593,
        "NI" : 85632599,
        "TH" : 85632293,
        "AW" : 85632295,
        "QA" : 85632299,
        "CL" : 85633057,
        "RU" : 85632685,
        "CA" : 85633041,
        "GN" : 85632691,
        "MA" : 85632693,
        "CN" : 85632695,
        "AU" : 85632793,
        "NZ" : 85633345,
        "MO" : 85632161,
        "KW" : 85632401,
        "BE" : 85632997,
        "CZ" : 85633105,
        "BG" : 85633001,
        "MT" : 85633331,
        "UA" : 85633805,
        "PL" : 85633723,
        "GL" : 85633217,
        "UN" : 102312305,
        "XX" : -1,
        ""   : -1
    }

    #placetype lookup list
    geonames_org_placetype = {
        "ADM1"  : "region",
        "ADM1H" : "region",            # this should be marked CESSATION DATE with today's date, and MZ:IS_CURRENT = 0
        "ADM2"  : "county",
        "ADM2H" : "county",            # this should be marked CESSATION DATE with today's date, and MZ:IS_CURRENT = 0
        "ADM3"  : "localadmin",
        "ADM3H" : "localadmin",        # this should be marked CESSATION DATE with today's date, and MZ:IS_CURRENT = 0
        "ADM4"  : "localadmin",
        "ADM4H" : "localadmin",        # this should be marked CESSATION DATE with today's date, and MZ:IS_CURRENT = 0
        "ADM5"  : "localadmin",
        "ADMD"  : "localadmin",
        "ADMDH" : "localadmin",        # this should be marked CESSATION DATE with today's date, and MZ:IS_CURRENT = 0
        "ADMF"  : "locality",          # gov't building
        "PCL"   : "country",           # political entity
        "PCLD"  : "dependency",        # dependent political entity
        "PCLF"  : "dependency",        # freely associated state
        "PCLH"  : "country",           # historical political entity, CESSATION DATE with today's date, and MZ:IS_CURRENT = 0
        "PCLI"  : "country",           # independent political entity
        "PCLIX" : "region",            # section of independent political entity
        "PCLS"  : "dependency",        # semi-independent political entity
        "PPL"   : "locality",          # basic locality
        "PPLA"  : "locality",          # region capital      add new CAPITAL_OF list
        "PPLA2" : "locality",          # county capital      add new CAPITAL_OF list
        "PPLA3" : "locality",          # localadmin capital      add new CAPITAL_OF list
        "PPLA4" : "locality",          # localadmin capital      add new CAPITAL_OF list
        "PPLC"  : "locality",          # country capital      add new CAPITAL_OF list
        "PPLF"  : "locality",          # farm village
        "PPLG"  : "locality",          # seat of government of a political entity      add new CAPITAL_OF list
        "PPLH"  : "locality",          # historical populated place, CESSATION DATE with today's date, and MZ:IS_CURRENT = 0
        "PPLL"  : "locality",          # populated locality
        "PPLQ"  : "locality",          # abandoned populated place, CESSATION DATE with today's date, and MZ:IS_CURRENT = 0
        "PPLR"  : "locality",          # religious populated place
        "PPLS"  : "locality",          # populated places
        "PPLW"  : "locality",          # destroyed populated place, CESSATION DATE with today's date, and MZ:IS_CURRENT = 0
        "PPLX"  : "neighbourhood",
        "STLMT" : "locality"           # settlements
    }

    #placetypes that are "historical"
    #and need to be tagged as such
    historical_placetypes = {
        "ADM1H",
        "ADM2H",
        "ADM3H",
        "ADM4H",
        "ADMDH",
        "PCLH",
        "PPLH",
        "PPLQ",
        "PPLW"
    }

    #parent placetype lookup
    parent_placetype_lookup = {
        136251281   :  "dependency",
        85632163    :  "dependency",
        85632169    :  "dependency",
        85632421    :  "dependency",
        85632199    :  "dependency",
        85632611    :  "dependency",
        85632205    :  "dependency",
        85632629    :  "dependency",
        85632333    :  "dependency",
        85632641    :  "dependency",
        85632211    :  "dependency",
        85632731    :  "dependency",
        85632459    :  "dependency",
        85632653    :  "dependency",
        85632517    :  "dependency",
        85633153    :  "dependency",
        85633167    :  "dependency",
        85632473    :  "dependency",
        85632239    :  "dependency",
        85632677    :  "dependency",
        85632481    :  "dependency",
        85632485    :  "dependency",
        85632493    :  "dependency",
        874411115.  :  "region",
        85633729    :  "dependency",
        85632549    :  "dependency",
        85632789    :  "dependency",
        85632585    :  "dependency",
        85632587    :  "dependency",
        85632283    :  "dependency",
        85632697    :  "dependency",
        85632301    :  "dependency",
        85632167    :  "country",
        85632171    :  "country",
        85632173    :  "country",
        85632179    :  "country",
        85632303    :  "country",
        85632305    :  "country",
        85632403    :  "country",
        85632405    :  "country",
        85632181    :  "country",
        85632185    :  "country",
        85632187    :  "country",
        85632407    :  "country",
        85632189    :  "country",
        85632413    :  "country",
        85671209    :  "region",
        85632191    :  "country",
        85632425    :  "country",
        85632503    :  "country",
        85632307    :  "country",
        85632313    :  "country",
        85632315    :  "country",
        85632603    :  "country",
        85632605    :  "country",
        85632607    :  "country",
        85632609    :  "country",
        85632623    :  "country",
        85632317    :  "country",
        85632429    :  "country",
        85632319    :  "country",
        85632703    :  "country",
        85632431    :  "country",
        85632709    :  "country",
        85632505    :  "country",
        85632323    :  "country",
        85632625    :  "country",
        85632713    :  "country",
        85632203    :  "country",
        85632433    :  "country",
        85632627    :  "country",
        85632325    :  "country",
        85632635    :  "country",
        85632437    :  "country",
        85632207    :  "country",
        85632329    :  "country",
        85632331    :  "country",
        85632439    :  "country",
        85632335    :  "country",
        85632441    :  "country",
        85632715    :  "country",
        85632717    :  "country",
        85632721    :  "country",
        136251281   :  "dependency",
        85632443    :  "country",
        85632639    :  "country",
        85632213    :  "country",
        85632215    :  "country",
        85632217    :  "country",
        85632223    :  "country",
        85632449    :  "country",
        85632339    :  "country",
        85632343    :  "country",
        85632347    :  "country",
        85671199    :  "region",
        85632355    :  "country",
        85632729    :  "country",
        85632357    :  "country",
        85632643    :  "country",
        85632227    :  "country",
        85632451    :  "country",
        85632359    :  "country",
        85632645    :  "country",
        85632455    :  "country",
        85632461    :  "country",
        85632509    :  "country",
        85632735    :  "country",
        85632647    :  "country",
        85632465    :  "country",
        85633009    :  "country",
        85632511    :  "country",
        85632467    :  "country",
        85632229    :  "country",
        85632513    :  "country",
        85632361    :  "country",
        85632739    :  "country",
        85632747    :  "country",
        85632749    :  "country",
        85632657    :  "country",
        85632365    :  "country",
        85632369    :  "country",
        85632371    :  "country",
        85632519    :  "country",
        85632659    :  "country",
        85632373    :  "country",
        85632661    :  "country",
        85632379    :  "country",
        85632751    :  "country",
        85632663    :  "country",
        85633111    :  "country",
        85633121    :  "country",
        85632667    :  "country",
        85632671    :  "country",
        85632383    :  "country",
        85633129    :  "country",
        85633135    :  "country",
        85632231    :  "country",
        85633143    :  "country",
        85632385    :  "country",
        85671195    :  "region",
        85633147    :  "country",
        85633051    :  "country",
        85632469    :  "country",
        85633159    :  "country",
        85633163    :  "country",
        85632755    :  "country",
        85633171    :  "country",
        85632521    :  "country",
        85671203    :  "region",
        85632529    :  "country",
        85671191    :  "region",
        85632391    :  "country",
        85632757    :  "country",
        85632533    :  "country",
        85632235    :  "country",
        85633229    :  "country",
        85633237    :  "country",
        85632535    :  "country",
        85633241    :  "country",
        85633249    :  "country",
        85633253    :  "country",
        85632675    :  "country",
        85633259    :  "country",
        85633267    :  "country",
        85633269    :  "country",
        85632679    :  "country",
        85632681    :  "country",
        85632475    :  "country",
        85632761    :  "country",
        85632241    :  "country",
        85632483    :  "country",
        85633275    :  "country",
        85633279    :  "country",
        85633285    :  "country",
        85633287    :  "country",
        85632393    :  "country",
        85632487    :  "country",
        85632491    :  "country",
        85632541    :  "country",
        85633293    :  "country",
        85632495    :  "country",
        85632243    :  "country",
        85632245    :  "country",
        85632499    :  "country",
        85633337    :  "country",
        85632545    :  "country",
        85632547    :  "country",
        85632551    :  "country",
        85633735    :  "country",
        85632247    :  "country",
        85632395    :  "country",
        85633341    :  "country",
        85632553    :  "country",
        85633739    :  "country",
        85632249    :  "country",
        85632253    :  "country",
        85632397    :  "country",
        85633745    :  "country",
        85633813    :  "country",
        85633755    :  "country",
        85633763    :  "country",
        85633769    :  "country",
        85633779    :  "country",
        85632559    :  "country",
        85633789    :  "country",
        85632569    :  "country",
        85632257    :  "country",
        85632259    :  "country",
        85632571    :  "country",
        85632763    :  "country",
        85632765    :  "country",
        85632573    :  "country",
        85632261    :  "country",
        85632773    :  "country",
        85632263    :  "country",
        85632781    :  "country",
        85632785    :  "country",
        85632269    :  "country",
        85632271    :  "country",
        85632581    :  "country",
        85632583    :  "country",
        85632281    :  "country",
        85632285    :  "country",
        85632287    :  "country",
        85633793    :  "country",
        85632591    :  "country",
        85632593    :  "country",
        85632599    :  "country",
        85632293    :  "country",
        85632295    :  "country",
        85632299    :  "country",
        85633057    :  "country",
        85632685    :  "country",
        85633041    :  "country",
        85632691    :  "country",
        85632693    :  "country",
        85632695    :  "country",
        85632793    :  "country",
        85633345    :  "country",
        85632161    :  "country",
        85632401    :  "country",
        85632997    :  "country",
        85633105    :  "country",
        85633001    :  "country",
        85633331    :  "country",
        85633805    :  "country",
        85633723    :  "country",
        85633217    :  "country",
        102312305   :  "country"
    }

    #lets set up a timer
    counter = 0

    for row in reader:
        #show count to debug
        counter += 1
        if counter % 1000 == 0:
            print '\n'
            print counter
            print '\n'

        #read in all properties
        id = row['id']
        number = row['number']
        geonameid = row['geonameid']
        name = row['name']
        asciiname = row['asciiname']
        alternatenames = row['alternatenames']
        latitude = row['latitude']
        longitude = row['longitude']
        feature_class = row['feature_class']
        feature_code = row['feature_code']
        country_code = row['country_code']
        cc2 = row['cc2']
        admin1_code = row['admin1_code']
        admin2_code = row['admin2_code']
        admin3_code = row['admin3_code']
        admin4_code = row['admin4_code']
        population = row['population']
        elevation = row['elevation']
        dem = row['dem']
        timezone = row['timezone']
        modification_date = row['modification_date']

        #for this go around, only import P class
        if feature_class in ['P']:

            #this is a variable we'll use later to ensure we can actually import
            importable = True

            #we're not loading in a new feature, we're creating one from scratch this time...
            feature = {
                "type":        "Feature",
                "properties":  {},
                "bbox":        {},
                #we know all features are points, so...
                "geometry": {"coordinates":[float(longitude),float(latitude)],"type":"Point"}
            }

            #create variables for existing props and geom to store later (geom moves to alt)
            props = feature['properties']
            geom = feature['geometry']

            #first, lets figure out the placetype...
            for k,v in geonames_org_placetype.items():
                if feature_code == k:
                    props['wof:placetype'] = v

            #we do not want to import region, dependency, country, and other top-level
            #placetypes, so add a check here to not import them
            #
            #also ensure that a placetype has been added
            if not props.has_key('wof:placetype'):
                importable = False
                err = 'no placetype: '
            
            #localities only
            if importable:
                if not props['wof:placetype'] in ['locality']:
                    importable = False
                    err = 'not importable placetype: '

            #now, lets only work on rows that are importable
            if importable:

                props['wof:id'] = int(id)
                feature['id'] = int(id)

                #parent id
                props['wof:parent_id'] = -1

                for k,v in country_code_id_lookup.items():
                    if country_code == k:
                        props['wof:parent_id'] = v

                #is_current
                props['mz:is_current'] = -1

                #wof name
                props['wof:name'] = asciiname

                #country codes
                props['iso:country'] = country_code
                props['wof:country'] = country_code

                #src geom
                props['src:geom'] = 'geonames'

                #concordances
                props['wof:concordances'] = {'gn:id':int(geonameid)}

                #build up the hierarchy, since whos knows when we'll PIP..
                props['wof:hierarchy'] = []
                
                #take care of historical records
                if feature_code in historical_placetypes:
                    props['edtf:cessation'] = datetime.datetime.today().strftime('%Y-%m-%d')
                    props['mz:is_current'] = 0

                found_hier = False

                if not found_hier:
                    for k,v in parent_placetype_lookup.items():
                        if int(props['wof:parent_id']) == k:
                            props['wof:hierarchy'].append({str(v)+'_id':int(k)})
                            found_hier = True

                #population, src population, population rank
                if not int(population) < 1:
                    props['wof:population'] = int(population)
                    props['src:population'] = 'geonames'
                    if int(population) >= 10000000: 
                        props['wof:population_rank'] = 14
                    elif int(population)>= 5000000:
                        props['wof:population_rank'] = 13
                    elif int(population)>= 1000000:
                        props['wof:population_rank'] = 12
                    elif int(population) >= 500000:
                        props['wof:population_rank'] = 11
                    elif int(population) >= 200000:
                        props['wof:population_rank'] = 10
                    elif int(population) >= 100000:
                        props['wof:population_rank'] = 9
                    elif int(population) >= 50000:
                        props['wof:population_rank'] = 8
                    elif int(population) >= 20000:
                        props['wof:population_rank'] = 7
                    elif int(population) >= 10000:
                        props['wof:population_rank'] = 6
                    elif int(population) >= 5000:
                        props['wof:population_rank'] = 5
                    elif int(population) >= 2000:
                        props['wof:population_rank'] = 4
                    elif int(population) >= 1000:
                        props['wof:population_rank'] = 3
                    elif int(population) >= 200:
                        props['wof:population_rank'] = 2
                    elif int(population) > 0:
                        props['wof:population_rank'] = 1
                    else:
                        props['wof:population_rank'] = 0

                #gn properties
                #dont import any empty/null val props
                if len(geonameid) > 0:
                    props['gn:geonameid'] = int(geonameid)             #int
                if len(name) > 0:
                    props['gn:name'] = name                            #str
                if len(asciiname) > 0:
                    props['gn:asciiname'] = asciiname                  #str
                if len(latitude) > 0:
                    props['gn:latitude'] = float(latitude)             #float
                if len(longitude) > 0:
                    props['gn:longitude'] = float(longitude)           #float
                if len(feature_class) > 0:
                    props['gn:feature_class'] = feature_class          #str
                if len(feature_code) > 0:
                    props['gn:feature_code'] = feature_code            #str
                if len(country_code) > 0:
                    props['gn:country_code'] = country_code            #str
                if len(cc2) > 0:
                    props['gn:cc2'] = cc2                              #str
                if len(admin1_code) > 0:
                    props['gn:admin1_code'] = admin1_code              #str (could be int, but other codes in wof are str)
                if len(admin2_code) > 0:
                    props['gn:admin2_code'] = admin2_code              #str (could be int, but other codes in wof are str)
                if len(admin3_code) > 0:
                    props['gn:admin3_code'] = admin3_code              #str (could be int, but other codes in wof are str)
                if len(admin4_code) > 0:
                    props['gn:admin4_code'] = admin4_code              #str (could be int, but other codes in wof are str)
                if len(population) > 0:
                    props['gn:population'] = int(population)           #int
                if len(elevation) > 0:
                    props['gn:elevation'] = elevation                  #int (says int, but often null or blank. string val)
                if len(dem) > 0:
                    props['gn:dem'] = int(dem)                         #int
                if len(timezone) > 0:
                    props['gn:timezone'] = timezone                    #str
                if len(modification_date) > 0:
                    props['gn:modification_date'] = modification_date  #str

                #rebuild props
                feature['properties'] = props

                #write out new feature, check id just in case
                if not props['wof:id'] < 0:
                    if not len(str(props['wof:id'])) > 11:
                        exporter.export_feature(feature)

        #err checking
                    else:
                        print '\r'
                        print 'ERROR: JUNK ID, IMPORT FAILED.'
                        print '\r'

                else:
                    print '\r'
                    print 'ERROR: JUNK ID, IMPORT FAILED.'
                    print '\r'

            else:
                print err + str(geonameid)

        else:
            print 'not importable placetype: ' + str(geonameid)
