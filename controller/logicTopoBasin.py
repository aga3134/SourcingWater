from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp
from waterswak.flwdir import *
from colour import Color

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
fd=None

#load cx_dict
filename="data/catchment.json"
data = load_json_local(filename)
cx_dicts = {}
for i in range(len(data)):
    cx_dicts[data[i]['basin_id']]=data[i]
#print(cx_dicts)

class LogicTopoBasin():
    def FindBasinByID(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        sql = "select basin_no,basin_name as title,area,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from basin where basin_no='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無流域資料"}
        row = dict(row)

        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = [
            {
                "type": "line",
                "paint": {
                    "line-color":"#fff",
                    "line-width":3
                }
            }
        ]
        return {
            "nodeID":nodeID,
            "nodeName":row["title"]+"流域",
            "data":[row]
        }

    def FindMainRiverByID(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        #目前資料庫只有頭前溪主河道，先用這個測試
        sql = "select ogc_fid,ST_AsGeoJson(geom)::json as geom from c1300 limit 1;"
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無主流資料"}
        row = dict(row)

        row["title"] = "頭前溪"
        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = [
            {
                "type": "line",
                "paint":{
                    "line-color": "#f33",
                    "line-width": 4
                }
            }
        ]
        return {
            "nodeID":nodeID,
            "nodeName":"頭前溪",
            "setting":{
                "pathIndex":0
            },
            "data":[row]
        }

    def FindStreams(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]

        if nodeID not in cx_dicts:
            return {"error":"查無河道資料"}
        cx_dict = cx_dicts[nodeID]
        if "sto" in param:
            sto = int(param["sto"])
        else:
            sto = cx_dict['min_sto']
        #print(sto)
        
        fd = FlwDir()
        fd.reload(cx_dict["dtm"],cx_dict["ldd"])
        fd.init()

        row = {}
        row["title"] = cx_dict["basin_name"]+"河川細緻度"
        row["geom"] = json.loads(fd.streams(sto))
        row["layer"] = [
            {
                "type": "line",
                "paint":{
                    "line-color": "#f33",
                    "line-width": 2
                }
            }
        ]
        return {
            "nodeID":nodeID,
            "nodeName":cx_dict["basin_name"],
            "setting":{
                "inputConfig":[
                    {
                        "name":"河川細緻度",
                        "variable": "sto",
                        "value": sto,
                        "type": "number",
                        "min": 4,
                        "max": 11,
                        "step": 1
                    }
                ]
            },
            "data":[row]
        }

    def FindSubBasins(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        
        if nodeID not in cx_dicts:
            return {"error":"查無流域分區資料"}
        cx_dict = cx_dicts[nodeID]
        if "sto" in param:
            sto = param["sto"]
        else:
            sto = cx_dict['min_sto']
        
        fd = FlwDir()
        fd.reload(cx_dict["dtm"],cx_dict["ldd"])
        fd.init()

        row = {}
        row["title"] = cx_dict["basin_name"]+"流域細緻度"
        row["geom"] = json.loads(fd.subbasins_streamorder(sto))

        #setup color
        startColor = Color("#edf5fc")
        endColor = Color("#084286")
        colorList = list(startColor.range_to(endColor,len(row["geom"]["features"])))
        for (i,feat) in enumerate(row["geom"]["features"]):
            feat["properties"]["color"] = colorList[i].hex
        
        row["layer"] = [
            {
                "type": "fill",
                "paint":{
                    "fill-color": ["get","color"],
                    "fill-opacity": 0.5
                }
            }
        ]
        return {
            "nodeID":nodeID,
            "nodeName":cx_dict["basin_name"],
            "data":[row]
        }
