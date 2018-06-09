from __future__ import division
import json
import csv
import urllib2
import math
import matplotlib.pyplot as plt
import random
import numpy as np
import scipy.optimize
from scipy import stats

# Mercator projection, from:
# https://github.com/hrldcpr/mercator.py
import mercator

from shapely.geometry import MultiPoint

def get_area(points):
    poly = MultiPoint(points).convex_hull
    return poly.area

def run_analysis(region="us", ablated=False):
    def test_in_circle(point,circle):
        x, y = point
        xc, yc, r = circle
        d = (x - xc)**2 + (y - yc)**2
        return d <= ((r**2)+.000001)

    # circle-circle intersection algorithm, from:
    # https://gist.github.com/xaedes/974535e71009fa8f090e
    def circle_intersection(circle1, circle2):
        x1,y1,r1 = circle1
        x2,y2,r2 = circle2
        dx,dy = x2-x1,y2-y1
        d = math.sqrt(dx*dx+dy*dy)
        if d > r1+r2:
            return None # circles are separate
        if d < abs(r1-r2):
            return None # one circle is contained within the other
        if d == 0 and r1 == r2:
            return None # circles are coincident

        a = (r1*r1-r2*r2+d*d)/(2*d)
        h = math.sqrt(r1*r1-a*a)
        xm = x1 + a*dx/d
        ym = y1 + a*dy/d
        xs1 = xm + h*dy/d
        xs2 = xm - h*dy/d
        ys1 = ym - h*dx/d
        ys2 = ym + h*dx/d

        return (xs1,ys1),(xs2,ys2)

    def to_x_y(lat, lng):
        return mercator.get_lat_lng_tile(lat, lng, 0)
    def to_lat_lng(x, y):
        return mercator.get_tile_lat_lng(0, x, y)

    # dist in x,y * (6371 / 256 * 1.3) = dist in real life

    us_lat = 40.0 #degrees
    western_europe_lat = 51.5
    # From basis of Mercator projection:
    dist_factor = 6371.0 / 256.0 * (1.0/math.cos(math.radians(us_lat))) * 1000.0

    # xy_dist * dist_factor = km

    # Fitting a line while underestimating, adapted from:
    # https://stackoverflow.com/questions/14490400/line-fitting-below-points
    def fit_below(x, y) :
        if ablated:
            return .01, 0.0
        
        idx = np.argsort(x)
        x = x[idx]
        y = y[idx]

        def error_function_2(b, x, y) :
            a = np.min((y - b) / x)
            return np.sum((y - a * x - b)**2)

        cs = {"type":"ineq", "fun":lambda x: x}
        b = scipy.optimize.minimize(error_function_2, [0], args=(x, y), constraints=cs).x[0]

        a = np.min((y - b) / x)

        return a, b
        

        '''
        #slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
        #m = np.sum(y)/np.sum(x)
        #if m < .01:
        #    m = .01
        return .01, 0.0
        '''
        

    def distance(origin, destination):
        lat1, lon1 = origin
        lat2, lon2 = destination
        x1,y1 = to_x_y(lat1, lon1)
        x2,y2 = to_x_y(lat2, lon2)
        d_comp = math.sqrt((x1-x2)**2+(y1-y2)**2)
        return d_comp*dist_factor

    ping_mins = json.load(open("ping_mins.json","r"))
    anchor_onlyrelevant = json.load(open("anchor_onlyrelevant.json","r"))
    #anchors = list(sorted(anchor_onlyrelevant.keys()))
    #anchors = filter(lambda a: a[:2] == "us", anchors)
    us_anchors  = '''us-abn-as43996
us-abn-as51468
us-abn-as54054
us-atl-as2914
us-bcb-as1312
us-bos-as111
us-bos-as26167
us-cax-as14907
us-dal-as2914
us-dal-as7366
us-den-as7922
us-els-as40528
us-fcn-as32934
us-lan-as32244
us-lax-as15133
us-lax-as63403
us-ljl-as195
us-lwc-as2495
us-mia-as2914
us-mia-as33280
us-mnz-as30633
us-pao-as1280
us-pct-as88
us-phx-as53824
us-pou-as6124
us-qas-as14907
us-qas-as393246
us-rno-as3851
us-rtv-as16876
us-sea-as2914
us-sfo-as14061
us-sfo-as14907
us-sfo-as7203
us-sgu-as46309
us-sjc-as22300
us-wct-as7922'''.split('\n')

    western_europe_anchors = '''nl-hrd-as34612
ie-ork-as2128
nl-ams-as43996
nl-ede-as12859
uk-slo-as202109
nl-ams-as34106
es-bcn-as13041
fr-tin-as196670
ie-dub-as2128
fr-par-as5377
fr-zdb-as35625
uk-boh-as196745
nl-haa-as201682
nl-dft-as31019
nl-ams-as1200
lu-kay-as35733
fr-ysd-as8426
nl-utc-as1103
be-lln-as2611
ie-dub-as1213
nl-bst-as8211
uk-lon-as5607
be-anr-as2611
nl-ams-as286
nl-ams-as3333-2
uk-lba-as33920
nl-arn-as1140
ie-caw-as39122
uk-did-as786
lu-ezt-as2602
nl-ams-as1101
uk-slo-as43996
uk-lcy-as20965
fr-par-as57734
nl-ens-as1133
nl-haa-as60781
fr-sxb-as8839
uk-lon-as5459
uk-blt-as25376
fr-prm-as513
uk-slo-as5607
nl-bxt-as8211
fr-ysd-as201958
uk-lon-as34587
nl-ams-as3265
nl-dro-as51430
nl-ams-as12041
fr-tls-as39405
uk-lon-as8676
nl-roo-as43350
es-leg-as766
nl-ams-as35733
nl-dro-as12414
uk-lon-as6908'''.split("\n")

    anchors = us_anchors

    if region == "we":
        anchors = western_europe_anchors
        dist_factor = 6371.0 / 256.0 * (1.0/math.cos(math.radians(western_europe_lat))) * 1000.0


    bestlines = {}

    def simpleplot(data):
        plt.scatter(map(lambda x:x[0], data), map(lambda x:x[1], data), s=1)
        plt.show()

    def myplot(dists, rtts, line=None):
        samp = zip(dists, rtts)#random.sample(points, 100)

        plt.scatter(map(lambda x:x[0], samp), map(lambda x:x[1], samp), s=.1)
        plt.plot([0, 20000], [0, 200], 'k-', lw=1.0)
        if line is not None:
            #print 4500*line[0], line[1]
            plt.plot([0, 20000], [line[1], 20000*line[0]+line[1]], 'g:', lw=1.0)
        plt.xlabel('Distance (km)', fontsize=12)
        plt.ylabel('RTT (ms)', fontsize=12)
        plt.xlim([0,4500])
        plt.ylim([0,90])
        plt.show()

    def get_bestlines_excl_targ(target):
        bestlines = {}
        for source in anchors:
            if source == target:
                continue
            rtts = []
            dists = []
            for dest in anchors:
                if dest == target:
                    continue
                try:
                    rtt = ping_mins[dest][source]
                except:
                    continue
                if rtt >= 100000.0 - 1:
                    continue
                if source == dest:
                    continue
                geo_dest = anchor_onlyrelevant[dest]
                geo_source = anchor_onlyrelevant[source]
                p1 = (geo_source["lat"],geo_source["lng"])
                p2 = (geo_dest["lat"],geo_dest["lng"])
                dist = distance(p1,p2) 
                rtts.append(rtt)
                dists.append(dist)
            #myplot(dists, rtts)
            if len(rtts) > 1:
                m, b = fit_below(np.array(dists), np.array(rtts))
                bestlines[source] = (m,b)
                #myplot(dists, rtts, (m,b))
        return bestlines

    GAMMA = 50.0 / dist_factor

    errors = []

    #simpleplot(bestlines.values())
    for target in anchors:
        #print "target:", target
        
        # DO NOT USE in below *calculation* - this is the goal!
        ##########
        geo_target_ANS = anchor_onlyrelevant[target]
        target_ANS = (geo_target_ANS["lat"],geo_target_ANS["lng"])
        ##########
        circles = []
        blines = get_bestlines_excl_targ(target)
        
        for landmark in anchors:
            try:
                rtt = ping_mins[target][landmark]
            except:
                continue
            if rtt >= 100000.0 - 1:
                continue
            if target == landmark:
                continue
            geo_landmark = anchor_onlyrelevant[landmark]
            p1 = (geo_landmark["lat"],geo_landmark["lng"])

            
            m,b = blines[landmark]

            # in km
            estimated_dist = (rtt - b) / m
            # in xy
            radius = estimated_dist / dist_factor
            x,y = to_x_y(p1[0], p1[1])
            circles.append((x,y,radius+GAMMA))

        C = len(circles)
        # contains only the circles that actually intersect
        good_circles = set()
        #print C
        intersection_points = []
        for i in range(C):
            for j in range(i,C):
                res = circle_intersection(circles[i], circles[j])
                if res is None:
                    pass
                    #print "eep", circles[i], circles[j]
                else:
                    intersection_points.append(res[0])
                    intersection_points.append(res[1])
                    good_circles.add(circles[i])
                    good_circles.add(circles[j])
        #print len(intersection_points)
        #print len(good_circles), C
        #print "------"

        if len(good_circles) == 0: # if we had no ping data at all, we can move on
            #print ":(", C
            #print "--"
            continue
        
        polygon_points = []
        for t in [1.0, 1.05, 1.10, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]:
            for ip in intersection_points:
                ct = 0
                in_all = True
                for circle in good_circles:
                    circle = (circle[0], circle[1], circle[2]*t)
                    if not test_in_circle(ip,circle):
                        in_all = False
                    else:
                        ct += 1
                if in_all:
                    polygon_points.append(ip)
            if len(polygon_points) > 0:
                break
        P = float(len(polygon_points))
        if len(polygon_points) == 0:
            print ":S", target
            continue
        #print t

        # get centroid
        xh = sum(map(lambda p: p[0], polygon_points)) / P
        yh = sum(map(lambda p: p[1], polygon_points)) / P

        guess = to_lat_lng(xh, yh)
        
        # Does the error calculation, can use target_ANS
        ##########
        error = distance(guess, target_ANS)
        errors.append(error)
        ##########

        #print error
        #print "--"
        #print str(round(get_area(polygon_points)*dist_factor, 2))
        #print error

    errs = sorted(errors)
    return errs

def myplot(errs, mark="k-"):
    E = len(errs)
    y = np.array(range(0,E+1))/float(E)
    x = [0] + errs
    #plt.scatter(map(lambda x:x[0], samp), map(lambda x:x[1], samp), s=1)
    return plt.plot(x, y, mark, lw=.5)
    #plt.plot([0, 4500], [0, 70], 'k-', lw=0.5, ls='dashed')

def saveplot(name, pl1, pl2):
    plt.xlabel('Error Distance (km)', fontsize=12)
    plt.ylabel('Cumulative Probability', fontsize=12)

    #plt.xlim([0,4500])
    #plt.ylim([0,90])
    plt.legend([pl1, pl2], ["CBG", "ablated"], loc=4)
    plt.xlim([0,600])
    plt.xticks(np.arange(0, 700, step=100))
    plt.ylim([0,1])
    plt.yticks(np.arange(0, 1.1, step=0.1))
    #plt.show()
    plt.savefig(name, bbox_inches='tight', dpi=300)
    
def med(errs):
    return np.median(errs)

# running US
us_na = run_analysis("us", ablated=False)
print "Median Error for US, no ablation (km):", med(us_na)
pl1, = myplot(us_na, "k-")
# runnnig US ablated
us_ab = run_analysis("us", ablated=True)
print "Median Error for US, with ablation (km):", med(us_ab)
pl2, = myplot(us_ab, "k--")
saveplot("figure3a.png", pl1, pl2)

plt.clf()

# running Western Europe
we_na = run_analysis("we", ablated=False)
print "Median Error for Western Europe, no ablation (km):", med(we_na) 
pl3, = myplot(we_na, "k-")
# running Western Europe ablated
we_ab = run_analysis("we", ablated=True)
print "Median Error for Western Europe, with ablation (km):", med(we_ab)
pl4, = myplot(we_ab, "k--")
saveplot("figure3b.png", pl3, pl4)
