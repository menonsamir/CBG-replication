import json
import csv
import urllib2
import math
import matplotlib.pyplot as plt
import random

from datetime import datetime
import time

############################################################
#################         CONFIG        ####################
############################################################
START_DATE = datetime(2018,1,29,10,49,35)                 ##
STOP_DATE =   datetime(2018,1,29,10,53,35)                ##
DO_FETCH = False                                          ##
############################################################


# Haversine distance formula, from:
# https://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
def distance(origin, destination):
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d


s = '''at-vie-as1853
ch-zrh-as34288
ch-zrh-as559
cz-prg-as25192
de-ber-as25291
de-ham-as12731
fi-tmp-as29432
fr-cdg-as2486
ie-dub-as2128
it-trn-as12779
lu-lux-as2602
nl-ams-as3333
no-osl-as39029
sk-bts-as2607
us-bos-as11488
nl-ams-as3333-2
de-muc-as5539
fr-sxb-as8839
us-pao-as5580
de-fra-as5580
nl-dft-as31019
us-ewr-as5580
gr-ath-as5408
uk-lcy-as20965
uk-cdf-as48294
fr-zdb-as35625
rs-beg-as13004
nl-ams-as1101
is-rey-as1850
jp-tyo-as2500
pl-poz-as9112
de-str-as553
fi-hel-as3292
se-sto-as59521
fr-vbn-as199422
hu-bud-as12303
is-rey-as25509
nl-arn-as1140
at-vie-as1120
fr-prm-as513
au-mel-as38796
us-pao-as1280
ru-mow-as47764
ie-caw-as39122
es-bcn-as13041
se-sto-as8674
ie-dub-as1213
de-kel-as13101
tn-tun-as5438
uy-mvd-as28000
za-jnb-as10474
au-bne-as4608
cz-prg-as39392
fr-tin-as196670
be-lln-as2611
mu-plu-as327681
de-fra-as8763
us-dal-as2914
us-mia-as2914
se-got-as50168
ru-mow-as15835
us-sea-as2914
us-atl-as2914
us-dal-as7366
cz-prg-as2852
dk-blp-as59469
be-anr-as2611
uk-lon-as60157
us-wct-as7922
de-cal-as39702
us-sfo-as14061
uk-slo-as202109
nz-hlz-as681
sg-sin-as133165
de-ett-as202040
nl-ams-as3265
us-den-as7922
de-nue-as33988
nl-ams-as12041
kz-ala-as21299
sk-bts-as201702
si-lzp-as198644
kz-plx-as21282
lk-cmb-as38229
nl-ams-as43996
uk-slo-as43996
qa-doh-as8781
uk-lon-as5459
us-qas-as14907
us-cax-as14907
it-mil-as16004
us-sfo-as14907
sg-sin-as45494
us-lan-as32244
uk-lon-as8676
br-sao-as22548
us-qas-as10745
us-phx-as53824
se-sln-as49515
dk-blp-as39839
sk-bts-as29405
de-fra-as48918
ua-iev-as29632
in-bom-as33480
de-str-as48918
dk-blp-as197495
cz-brq-as197451
ee-jvi-as198068
bg-sof-as197216
nl-ens-as1133
np-ktm-as45170
ch-gtg-as20612
de-ber-as20647
fr-par-as57734
rs-ini-as13303
fi-jyv-as30798
at-klu-as42473
nz-lyj-as17746
us-sjc-as22300
de-muc-as8767
es-leg-as766
us-els-as40528
nl-dro-as51430
us-pou-as6124
pk-isb-as7590
nl-hrd-as34612
us-rtv-as16876
at-szg-as5404
ph-qzt-as9821
fr-ysd-as201958
de-fra-as49024
de-ham-as201709
mv-mle-as7642
nl-ams-as3333-preprod
bd-dac-as24122
sg-sin-as18106
us-qas-as393246
us-lax-as63403
ca-van-as852
de-fra-as43996
us-abn-as43996
hk-hkg-as43996
nl-haa-as60781
us-mia-as33280
ca-mtr-as852
sg-sin-as43996
cz-prg-as6881
nl-haa-as201682
de-fra-as28753
mn-uln-as45204
ro-buh-as39107
us-mnz-as30633
us-sfo-as7203
sg-sin-as59253
jp-tyo-as13901
de-gaa-as56357
cl-scl-as27678
pe-lim-as27843
nc-nou-as56055
bg-sof-as47872
bg-sls-as198228
fr-ysd-as8426
de-erl-as680
cr-sjo-as263779
nl-roo-as43350
id-jkt-as10208
ar-bue-as4270
de-nue-as60574
uk-boh-as196745
at-vie-as30971
uk-lon-as6908
nl-utc-as1103
za-umr-as37668
nl-dro-as12414
ru-led-as43317
de-drs-as42699
za-jnb-as37474
fo-hyv-as15389
uk-lba-as33920
de-ber-as62310
bt-thi-as38740
cz-prg-as52130
de-dar-as8365
za-cpt-as37663
ee-tll-as51349
uk-lon-as5607
uk-slo-as5607
hk-hkg-as133752
fi-hel-as3274
cz-brq-as24971
nl-ams-as1200
uk-blt-as25376
ca-wtl-as4508
ie-ork-as2128
lv-rix-as52048
dk-taa-as51468
ie-dub-as2128
us-rno-as3851
ru-mot-as13238
de-bwe-as680
nl-ams-as35733
us-abn-as51468
kh-pnh-as7712
us-abn-as54054
us-sgu-as46309
lu-kay-as35733
de-ham-as35258
ua-iev-as24725
ca-wnp-as18451
de-dus-as12676
uk-lon-as34587
us-lax-as15133
us-lwc-as2495
lb-bey-as12812
pg-pom-as17828
ch-zrh-as9092
nl-ams-as34106
dk-hje-as39642
us-bos-as26167
us-pct-as88
tz-dar-as327844
dk-aal-as9158
au-syd-as135150
dk-cph-as9158
ca-wnp-as16395
us-ljl-as195
nz-akl-as38064
us-bos-as111
kw-kwi-as42961
ke-nbo-as37578
nl-ede-as12859-client
it-rom-as24796
us-fcn-as32934
nl-ede-as12859
de-che-as21413
de-ham-as12731
py-slo-as27733
uk-did-as786
nl-bst-as8211
nl-bxt-as8211
nz-wlg-as9834
lt-vno-as21412
de-ber-as25291
us-bcb-as1312
fi-hel-as6667
lu-ezt-as2602
de-kae-as8560'''.split("\n")

def merge_two_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z

'''
anchor_to_probe_raw = csv.reader(open("from_anchor_to_probe.csv", 'r'), delimiter=',')

anchor_info = {}

for r in anchor_to_probe_raw:
    #print r[1],r[2]
    anchor_info[r[1]] = {'probe':r[2], 'city':r[3], 'country':r[4]}

json.dump(anchor_info, open("anchor_info.json","w"))

'''

'''
anchor_info_detail = {}

import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    getattr(ssl, '_create_unverified_context', None)): 
    ssl._create_default_https_context = ssl._create_unverified_context

anchor_info = json.load(open("anchor_info.json","r"))

    myurl = "http://atlas.ripe.net/api/v2/probes/"+str(p['probe'])+"/?format=json"
    result = json.loads(urllib2.urlopen(myurl).read())
    print k
    anchor_info_detail[k] = merge_two_dicts(p, {"probe_details":result})

json.dump(anchor_info_detail, open("anchor_info_detail.json","w"))
'''

'''
anchor_info_detail = json.load(open("anchor_info_detail.json","r"))
anchor_onlyrelevant = {}
for k in anchor_info_detail:
    p = anchor_info_detail[k]
    cs = p["probe_details"]["geometry"]["coordinates"]
    z = {"lat": cs[1], "lng": cs[0]}
    anchor_onlyrelevant[k] = z
json.dump(anchor_onlyrelevant, open("anchor_onlyrelevant.json","w"))
'''

start = str(int(time.mktime(START_DATE.timetuple())))
stop = str(int(time.mktime(STOP_DATE.timetuple())))

print START_DATE, STOP_DATE
print "--"

anchor_to_probe = json.load(open("anchor_info.json","r"))
probe_to_anchor = {}
for anchor in anchor_to_probe:
    probe_to_anchor[anchor_to_probe[anchor]["probe"]] = anchor

o = json.load(open("measurement_urls.json", "r"))

pings = {}
ping_mins = {}

if DO_FETCH:
    for r in o['results']:
        #try:
        result_url = r['result']+"&start="+start+"&stop="+stop+"&anchors-only=true"
        dest = r['target'].split(".")[0]
        #if dest in s:
        #    continue
        try:
            readings = json.loads(urllib2.urlopen(result_url).read())
        except:
            print "unavailible for given time: ", dest
            continue
        #collected = {}
        collected_min = {}
        for reading in readings:
            source = probe_to_anchor[str(reading["prb_id"])]
            #if source not in collected:
            #    collected[source] = []
            if source not in collected_min:
                collected_min[source] = 100000.0
            #summary = {"max":reading["max"], "min":reading["min"], "measures": reading["result"]}
            #collected[source].append(summary)
            if float(reading["min"]) > 0.0:
                collected_min[source] = min(collected_min[source],float(reading["min"]))
        #pings[dest] = collected
        ping_mins[dest] = collected_min
        print dest
        #except:
        #    print "ERROR on", r['target']


#json.dump(pings, open("pings.json","w"))

if DO_FETCH:
    json.dump(ping_mins, open("ping_mins.json","w"))
else:
    ping_mins = json.load(open("ping_mins.json","r"))

anchor_onlyrelevant = json.load(open("anchor_onlyrelevant.json","r"))
anchors = list(sorted(anchor_onlyrelevant.keys()))
points = []
rtts = []
dists = []
print(len(anchors))
for anchor in anchors:
    for source in anchors:
        try:
            rtt = ping_mins[anchor][source]
        except:
            continue
        if rtt >= 100000.0 - 1:
            continue
        geo_anchor = anchor_onlyrelevant[anchor]
        geo_source = anchor_onlyrelevant[source]
        p1 = (geo_anchor["lat"],geo_anchor["lng"])
        p2 = (geo_source["lat"],geo_source["lng"])
        dist = distance(p1,p2)
        points.append((dist,rtt))
        rtts.append(rtt)
        dists.append(dist)
#json.dump(points, open("points.json","w"))

samp = points#random.sample(points, 100)

plt.scatter(map(lambda x:x[0], samp), map(lambda x:x[1], samp), c='k', facecolors='k', marker='s', s=.1, alpha=0.1)
plt.plot([0, 20000], [0, 200], 'k-', lw=0.5)
#plt.plot([0, 4500], [0, 70], 'k-', lw=0.5, ls='dashed')
plt.xlabel('Distance (km)', fontsize=12)
plt.ylabel('RTT (ms)', fontsize=12)
plt.xlim([0,4500])
plt.ylim([0,90])
#plt.show()
plt.savefig("figure1.png", dpi=300)

