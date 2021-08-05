
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
            f["id"] = p[idKey]
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