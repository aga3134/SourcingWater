
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