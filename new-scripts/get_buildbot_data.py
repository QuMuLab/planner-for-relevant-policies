import json
import urllib

from external.datasets import DataSet, DataItem
from reports import Table


def load_data(test):
    server = 'localhost:8010'
    url = 'http://' + server + '/json/builders/' + test + '/builds/_all'
    data = json.load(urllib.urlopen(url))
    return data

def parse_data(data):
    ds = DataSet()
    for build_id in data:
        times = data[build_id]['steps'][-1]['times']
        start_time = times[0]
        end_time = times[1]    
        properties = data[build_id]['properties']  
        for p in properties:
            if p[-1] == 'SetProperty Step':
                att = p[0]            
                satt = att.split('-', 3)
                what = satt[0]
                config = satt[1]
                domain = satt[2]
                problem = satt[3]                
                
                value = p[1]
                
                d = {'start_time':start_time, 
                     'end_time':end_time,
                     'what':what, 
                     'config': config, 
                     'domain':domain, 
                     'problem':problem, 
                     'value':value}
                di = DataItem(d)
                ds.append(di)
    return ds            

def build_tables():
    def tuple2string(t):
        s = ""
        for x in t:
            s = s + x + "/"
        return s    
    tables = {}
    for what, group in ds.groups("what"):
        t = Table(what)    
        for cfg, res in group.groups("config","domain","problem"):
            t.add_cell('title', tuple2string(cfg), 'title ' + tuple2string(cfg))        
            for r in res:
                t.add_cell(str(r['start_time']), tuple2string(cfg), r['value'])
        tables[what] = t
    return tables
        
d = load_data('nightly-test')
ds = parse_data(d)
ts = build_tables()

for t in ts:
    print ts[t]

#print_table(pd, cdp, 'expanded')
#print_table(pd, cdp, 'total_time')
