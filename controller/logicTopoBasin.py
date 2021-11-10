from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import DictToGeoJsonProp,InitFlow,MergeRowsToGeoJson
from controller.style import *
from colour import Color

class LogicTopoBasin():
    def FindBasinByID(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        sql = "select basin_no as id,basin_name as name,area,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from basin where basin_no='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無流域資料"}
        row = dict(row)

        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = BasinStyle(lineWidth=3)
        if "format" in param and param["format"] == "geojson":
            return row["geom"]
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "data":[row]
        }

    def FindMainRiverByID(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        #目前資料庫只有頭前溪主河道，先用這個測試
        sql = "select ogc_fid as id,ST_AsGeoJson(geom)::json as geom from c1300 limit 1;"
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無主流資料"}
        row = dict(row)

        row["id"] = nodeID
        row["name"] = "頭前溪"
        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = FlowPathStyle(lineWidth=4,color="#f33")
        if "format" in param and param["format"] == "geojson":
            return row["geom"]
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "setting":{
                "pathIndex":0
            },
            "data":[row]
        }

    def FindStreams(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]

        fd, cx_dict = InitFlow(nodeID)
        if fd is None:
            return {"error":"查無河道資料"}
        if "sto" in param:
            sto = int(param["sto"])
        else:
            sto = cx_dict['min_sto']
        #print(sto)

        row = {}
        row["id"] = nodeID
        row["name"] = cx_dict["basin_name"]
        row["geom"] = json.loads(fd.streams(sto))

        #setup color
        startColor = Color("#ff3333")
        endColor = Color("#3333ff")
        colorList = list(startColor.range_to(endColor,len(row["geom"]["features"])))
        for (i,feat) in enumerate(row["geom"]["features"]):
            feat["properties"]["color"] = colorList[i].hex

        row["layer"] = FlowPathStyle(lineWidth=1.5,colorKey="color")
        if "format" in param and param["format"] == "geojson":
            return row["geom"]
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "setting":{
                "inputConfig":[
                    {
                        "name":"河川級序",
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

        fd, cx_dict = InitFlow(nodeID)
        if fd is None:
            return {"error":"查無流域分區資料"}
        if "sto" in param:
            sto = int(param["sto"])
        else:
            sto = cx_dict['min_sto']

        row = {}
        row["id"] = nodeID
        row["name"] = cx_dict["basin_name"]
        row["geom"] = json.loads(fd.subbasins_streamorder(sto))

        #setup color
        startColor = Color("#edf5fc")
        endColor = Color("#084286")
        colorList = list(startColor.range_to(endColor,len(row["geom"]["features"])))
        for (i,feat) in enumerate(row["geom"]["features"]):
            feat["properties"]["color"] = colorList[i].hex
        
        row["layer"] = SubbasinStyle(fillKey="color")
        if "format" in param and param["format"] == "geojson":
            return row["geom"]
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "setting":{
                "inputConfig":[
                    {
                        "name":"河川級序",
                        "variable": "sto",
                        "value": sto,
                        "type": "number",
                        "min": 6,
                        "max": 11,
                        "step": 1
                    }
                ]
            },
            "data":[row]
        }

    def FindLivingArea(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        sql = "select basin_no,basin_name from basin where basin_no='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無流域資料"}

        #shape資訊不完整
        if not "shape" in param:
            return {
                "info":"請在流域內點選一個位置",
                "nodeID":nodeID,
                "nodeName":row["basin_name"],
                "setting":{
                    "shapeConfig":{
                        "type":"point",
                        "variable": "shape",
                        "num": 1,
                        "layer":SymbolStyle("marker-red",allowOverlap=True)
                    }
                }
            }
        shape = json.loads(param["shape"])

        #check if lat,lng in basin
        lat = shape["ptArr"][0][1]
        lng = shape["ptArr"][0][0]
        """sql = "select basin_no from basin where basin_no='%s' and ST_Contains(ST_Transform(ST_SetSRID(geom,3826),4326),ST_SetSRID(ST_POINT(%s,%s),4326));" % (nodeID,lng,lat)
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "位置需在流域內"}"""

        sql = "select countyname,townname,villname as id,villname as name,ST_AsGeoJson(ST_Transform(ST_SetSRID(sim_geom,3826),4326))::json as geom from village_moi_121 where ST_Contains(ST_Transform(ST_SetSRID(sim_geom,3826),4326),ST_SetSRID(ST_POINT(%s,%s),4326));" % (lng,lat)
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無村里資料"}
        row = dict(row)

        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = LivingAreaStyle()
        if "format" in param and param["format"] == "geojson":
            return row["geom"]
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "data":[row]
        }

    def FindAgricultureArea(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        sql = "select basin_no,basin_name from basin where basin_no='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無流域資料"}

        #shape資訊不完整
        if not "shape" in param:
            return {
                "info":"請在流域內點選一個位置",
                "nodeID":nodeID,
                "nodeName":row["basin_name"],
                "setting":{
                    "shapeConfig":{
                        "type":"point",
                        "variable": "shape",
                        "num": 1,
                        "layer":SymbolStyle("marker-red",allowOverlap=True)
                    }
                }
            }
        shape = json.loads(param["shape"])

        #check if lat,lng in basin
        lat = shape["ptArr"][0][1]
        lng = shape["ptArr"][0][0]
        """sql = "select basin_no from basin where basin_no='%s' and ST_Contains(ST_Transform(ST_SetSRID(geom,3826),4326),ST_SetSRID(ST_POINT(%s,%s),4326));" % (nodeID,lng,lat)
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "位置需在流域內"}"""

        sql = "select countyname,townname as id,townname as name,ST_AsGeoJson(ST_Transform(ST_SetSRID(sim_geom,3824),4326))::json as geom from town_moi where ST_Contains(ST_Transform(ST_SetSRID(sim_geom,3824),4326),ST_SetSRID(ST_POINT(%s,%s),4326));" % (lng,lat)
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無縣市資料"}
        row = dict(row)

        row["geom"] = DictToGeoJsonProp(row)
        row["layer"] = AgricultureAreaStyle()
        if "format" in param and param["format"] == "geojson":
            return row["geom"]
        return {
            "nodeID":row["id"],
            "nodeName":row["name"],
            "data":[row]
        }
    
    def FindIndustryArea(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        sql = "select basin_no,basin_name from basin where basin_no='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無流域資料"}

        #shape資訊不完整
        if not "shape" in param:
            return {
                "info":"請在流域內點選一個位置",
                "nodeID":nodeID,
                "nodeName":row["basin_name"],
                "setting":{
                    "shapeConfig":{
                        "type":"circle",
                        "variable": "shape",
                        "fixedRadius": 10000,
                        "layer":CircleStyle()
                    }
                }
            }
        shape = json.loads(param["shape"])

        #check if lat,lng in basin
        lat = shape["center"][1]
        lng = shape["center"][0]
        radius = shape["radius"]
        """sql = "select basin_no from basin where basin_no='%s' and ST_Contains(ST_Transform(ST_SetSRID(geom,3826),4326),ST_SetSRID(ST_POINT(%s,%s),4326));" % (nodeID,lng,lat)
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "位置需在流域內"}"""

        pt = "ST_Transform(ST_SetSRID(ST_POINT(%s,%s),4326),3826)" % (lng,lat)
        geom = "ST_SetSRID(geom,3826)"
        sql = """
            select fd as id,fname as name,type,catagory,
            ST_AsGeoJson(ST_Transform(%s,4326))::json as geom,
            ST_Distance(%s,%s) as dist
            from \"25598-台灣各工業區範圍圖資料集\" where
            ST_DWithin(%s,%s, %d)
            order by dist;
        """ % (geom,pt,geom,pt,geom,radius)

        rows = db.engine.execute(sql).fetchall()
        if len(rows) == 0:
            return {"error": "範圍內無工業區資料"}
        arr = []
        for row in rows:
            d = dict(row)
            d["geom"] = d["geom"]
            arr.append(d)

        geom = MergeRowsToGeoJson(arr,idKey="id",skipArr=["geom"])

        data = {}
        data["geom"] = geom
        data["layer"] = IndustryAreaStyle()
        if "format" in param and param["format"] == "geojson":
            return data["geom"]
        return {
            "nodeID":rows[0]["id"],
            "nodeName":rows[0]["name"],
            "data":[data]
        }

    def FindReservoir(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        sql = "select basin_no,basin_name from basin where basin_no='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無流域資料"}
        sql = "select res_name as id,res_name as name,ST_AsGeoJson(ST_Transform(ST_SetSRID(wkb_geometry,3826),4326))::json as geom from swresoir where basin_no='%s';" % (nodeID)
        rows = db.engine.execute(sql).fetchall()
        if len(rows) == 0:
            return {"error": "此流域查無水庫資料"}
        arr = []
        for row in rows:
            d = dict(row)
            d["geom"] = d["geom"]
            arr.append(d)

        geom = MergeRowsToGeoJson(arr,idKey="id",skipArr=["geom"])

        data = {}
        data["geom"] = geom
        data["layer"] = SymbolStyle("marker-blue",allowOverlap=True)
        if "format" in param and param["format"] == "geojson":
            return geom
        return {
            "nodeID":rows[0]["id"],
            "nodeName":rows[0]["name"],
            "data":[data]
        }

    def FindProtectArea(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        #內縮1公里以避免邊界誤差把鄰近區域算進來
        sql = "select basin_no,basin_name,ST_AsEWKT(ST_Buffer(geom,-1000)) as geom from basin where basin_no='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無流域資料"}

        basinGeom = "ST_SetSRID(ST_GeomFromEWKT('%s'),3826)" % row["geom"]
        sql = "select gid as id,polyname as name,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from twqprot where ST_Intersects(%s,ST_SetSRID(geom,3826));" % (basinGeom)
        #print(sql)
        rows = db.engine.execute(sql).fetchall()
        if len(rows) == 0:
            return {"error": "此流域查無水質水量保護區"}
        arr = []
        for row in rows:
            d = dict(row)
            d["geom"] = d["geom"]
            arr.append(d)

        geom = MergeRowsToGeoJson(arr,idKey="id",skipArr=["geom"])

        data = {}
        data["geom"] = geom
        data["layer"] = SubbasinStyle()
        if "format" in param and param["format"] == "geojson":
            return geom
        return {
            "nodeID":rows[0]["id"],
            "nodeName":rows[0]["name"],
            "data":[data]
        }

    def FindFloodArea(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]

        nodeName = ""
        if "nodeName" in param:
            nodeName = param["nodeName"]

        #內縮1公里以避免邊界誤差把鄰近區域算進來
        sql = "select basin_no,basin_name,ST_AsEWKT(ST_Buffer(geom,-1000)) as geom from basin where basin_no='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無流域資料"}

        if "rain" in param:
            rain = param["rain"]
        else:
            rain = "150mm_6hr"

        basinGeom = "ST_SetSRID(ST_GeomFromEWKT('%s'),3826)" % row["geom"]
        sql = "select gid as id,flood_dept,county,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from %s where ST_Intersects(%s,ST_SetSRID(geom,3826));" % ("flood_"+rain,basinGeom)
        #print(sql)
        rows = db.engine.execute(sql).fetchall()
        if len(rows) == 0:
            return {"error": "此流域查無淹水潛勢圖"}
        arr = []
        for row in rows:
            d = dict(row)
            d["geom"] = d["geom"]
            arr.append(d)

        geom = MergeRowsToGeoJson(arr,idKey="id",skipArr=["geom"])

        #setup color
        for (i,feat) in enumerate(geom["features"]):
            dept = feat["properties"]["flood_dept"]
            if dept == "0.3-0.5":
                feat["properties"]["color"] = "#33f"
            elif dept == "0.5-1.0":
                feat["properties"]["color"] = "#3f3"
            elif dept == "1.0-2.0":
                feat["properties"]["color"] = "#ff3"
            elif dept == "2.0-3.0":
                feat["properties"]["color"] = "#f93"
            elif dept == ">3.0":
                feat["properties"]["color"] = "#f33"

        data = {}
        data["geom"] = geom
        data["layer"] = FloodStyle(fillKey="color")
        if "format" in param and param["format"] == "geojson":
            return geom
        return {
            "nodeID":rows[0]["id"],
            "nodeName":nodeName+"淹水潛勢",
            "setting":{
                "inputConfig":[
                    {
                        "name":"雨量等級",
                        "variable": "rain",
                        "value": rain,
                        "type": "select",
                        "option": [
                            {"name":"6小時150mm","value":"150mm_6hr"},
                            {"name":"6小時250mm","value":"250mm_6hr"},
                            {"name":"6小時350mm","value":"350mm_6hr"},
                            {"name":"12小時200mm","value":"200mm_12hr"},
                            {"name":"12小時300mm","value":"300mm_12hr"},
                            {"name":"12小時400mm","value":"400mm_12hr"},
                            {"name":"24小時200mm","value":"200mm_24hr"},
                            {"name":"24小時350mm","value":"350mm_24hr"},
                            {"name":"24小時500mm","value":"500mm_24hr"},
                            {"name":"24小時650mm","value":"650mm_24hr"}
                        ]
                    }
                ]
            },
            "data":[data]
        }

    def FindDebris(self,param):
        if not "nodeID" in param:
            return {"error":"no id parameter"}
        nodeID = param["nodeID"]
        #內縮1公里以避免邊界誤差把鄰近區域算進來
        sql = "select basin_no,basin_name,ST_AsEWKT(ST_Buffer(geom,-1000)) as geom from basin where basin_no='%s';" % nodeID
        row = db.engine.execute(sql).first()
        if row is None:
            return {"error": "無流域資料"}

        basinGeom = "ST_SetSRID(ST_GeomFromEWKT('%s'),3826)" % row["geom"]
        sql = "select debrisno as id,debrisno as name,ST_AsGeoJson(ST_Transform(ST_SetSRID(wkb_geometry,3826),4326))::json as geom from debrisstream1726 where ST_Intersects(%s,ST_SetSRID(wkb_geometry,3826));" % (basinGeom)
        #print(sql)
        rows = db.engine.execute(sql).fetchall()
        if len(rows) == 0:
            return {"error": "此流域查無水土石流潛勢溪流"}
        arr = []
        for row in rows:
            d = dict(row)
            d["geom"] = d["geom"]
            arr.append(d)

        geom = MergeRowsToGeoJson(arr,idKey="id",skipArr=["geom"])

        data = {}
        data["geom"] = geom

        #setup color
        startColor = Color("#ff3333")
        endColor = Color("#3333ff")
        colorList = list(startColor.range_to(endColor,len(geom["features"])))
        for (i,feat) in enumerate(geom["features"]):
            feat["properties"]["color"] = colorList[i].hex

        data["layer"] = FlowPathStyle(lineWidth=2,hoverWidth=4,colorKey="color")
        if "format" in param and param["format"] == "geojson":
            return geom
        return {
            "nodeID":rows[0]["id"],
            "nodeName":rows[0]["name"],
            "data":[data]
        }