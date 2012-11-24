#!/usr/bin/python
# -*- coding: utf8 -*-

import cherrypy
import foursquare
import config
import json
import time
from lib.mysql_connect import connect_to_mysql
class Root:
    def __init__(self):
        self.mean_herenow = self._mean_of_herenow()
        pass
    
    
    def _mean_of_herenow(self):
        sql = "select mid_lat, mid_lng, sum(herenow) as herenow_sum, count(*) as cnt from herenow_region group by mid_lat,mid_lng;"
        cursor = connect_to_mysql()
        cursor.execute(sql)
        res = {}
        for r in cursor.fetchall():
            x = r['mid_lat']
            y = r['mid_lng']
            res[ (x,y) ] = float(r['herenow_sum']/(1+r['cnt']))
        return res
    def get_instagram_heatmap(self):
        sql = "select * from pics_count order by time desc limit 2000"
        cursor = connect_to_mysql()
        cursor.execute(sql)
        res = []
        tset = set()
        for r in cursor.fetchall():
            x = r['mid_lat']
            y = r['mid_lng']
            if (x,y) in tset:
                continue
            else:
                tset.add( (x,y))
            res.append( (r['mid_lat'], r['mid_lng'], r['pics_count']) )
            print r['pics_count']
        print len(tset)
        return json.dumps(res)
    get_instagram_heatmap.exposed = True

    def get_foursquare_heatmap(self):
        sql = "select * from herenow_region order by time desc limit 2000"
        cursor = connect_to_mysql()
        cursor.execute(sql)
        res = []
        tset = set()
        for r in cursor.fetchall():
            x = r['mid_lat']
            y = r['mid_lng']
            if (x,y) in tset:
                continue
            else:
                tset.add( (x,y))
            #res.append( (r['mid_lat'], r['mid_lng'], float (r['herenow'])*1.0 - self.mean_herenow[(x,y)] )  ) 
            res.append( (r['mid_lat'], r['mid_lng'], float (r['herenow'])*1.0)  ) 
        return json.dumps(res)
    get_foursquare_heatmap.exposed = True

global_conf = {
        'global':{'server.environment': 'production',
            'engine.autoreload_on': True,
            'engine.autoreload_frequency':5,
            'server.socket_host': '0.0.0.0',
            'server.socket_port':7887,
            }
        }

cherrypy.config.update(global_conf)
cherrypy.quickstart(Root(), '/', global_conf)
