from waterswak.flwdir import *

def DictToGeoJsonProp(d,geomKey = "geom"):
    geom = {
        "type": "Feature",
        "geometry": d[geomKey]
    }
    prop = {}
    for key in d:
        if key == geomKey:
            continue
        prop[key] = d[key]
    geom["properties"] = prop
    return geom

def MergeRowsToGeoJson(rows,idKey="",geomKey="geom",skipArr=[]):
    geom = {}
    geom["type"] = "FeatureCollection"
    geom["features"] = []
    for row in rows:
        d = dict(row)
        f = {}
        f["type"] = "Feature"
        f["geometry"] = d[geomKey]
        p = {}
        for key in d:
            if key in skipArr:
                continue
            p[key] = d[key]
        if idKey != "":
            f["id"] = hash(p[idKey])
        f["properties"] = p
        geom["features"].append(f)
    return geom

def ToFloat(s):
    try:
        if isinstance(s, float) or isinstance(s, int):
            return float(s)
        else:
            return float(s.replace(",",""))
    except ValueError:
        return float('NaN')


#flow direction related
def load_json_local(filename):
    data = None
    try:
        data_date = ""
        with open(filename , 'r', encoding='UTF-8') as json_file:
            data = json.load(json_file)
            return data
    except:
        print("%s:%s" %(filename,"EXCEPTION!"))
        return None

#load cx_dict
filename="data/catchment.json"
data = load_json_local(filename)
cx_dicts = {}
for i in range(len(data)):
    cx_dicts[data[i]['basin_id']]=data[i]
#print(cx_dicts)

def InitFlow(basinID):
    if basinID not in cx_dicts:
        return (None,None)
    cx_dict = cx_dicts[basinID]
    fd = FlwDir()
    fd.reload(cx_dict["dtm"],cx_dict["ldd"])
    fd.init()
    return (fd,cx_dict)