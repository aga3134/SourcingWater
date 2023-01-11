from sqlalchemy.sql.functions import func
from model.db import db
import json
from controller.util import MergeRowsToGeoJson
import requests
from controller.style import *

class LayerController():
    def GetBasin(self,param):
        sql = "select basin_no,basin_name,area,ST_AsGeoJson(ST_Transform(ST_SetSRID(geom,3826),4326))::json as geom from basin;"
        rows = db.engine.execute(sql)
        geom = MergeRowsToGeoJson(rows,idKey="basin_no",skipArr=["geom"])

        #generate json_def
        data = {
            "geom": geom,
            "layer": BasinStyle(fill=True)
        }
        if "format" in param and param["format"] == "geojson":
            return geom
        return {
            "layerName": "流域",
            "data": [data]
        }

    def GetRainStation(self,param):
        sql = "select * from r_rain_station;"
        rows = db.engine.execute(sql)
        arr = []
        for row in rows:
            d = dict(row)
            d["geom"] = {
                "type": "Point",
                "coordinates": [float(d["lon"]),float(d["lat"])]
            }
            arr.append(d)
        geom = MergeRowsToGeoJson(arr,idKey="stationID",skipArr=["geom","lat","lon"])
        
        #generate json_def
        data = {
            "geom": geom,
            "layer": SymbolStyle("rain-station"),
        }
        #print(data)
        if "format" in param and param["format"] == "geojson":
            return geom
        return {
            "layerName": "雨量站",
            "data": [data]
        }

    def GetFloodStation(self,param):
        sql = "select * from r_flood_station;"
        rows = db.engine.execute(sql)
        arr = []
        for row in rows:
            d = dict(row)
            d["geom"] = {
                "type": "Point",
                "coordinates": [float(d["lng"]),float(d["lat"])]
            }
            arr.append(d)
        geom = MergeRowsToGeoJson(arr,idKey="_id",skipArr=["geom","lat","lng"])

        #generate json_def
        data = {
            "geom": geom,
            "layer": SymbolStyle("flood-station"),
        }
        #print(data)
        if "format" in param and param["format"] == "geojson":
            return geom
        return {
            "layerName": "淹水測站",
            "data": [data]
        }

    def GetCommutag(self,config,param):
        if not "dataset" in param:
            #param["dataset"] = "60c0307db652fe1483444844" #頭前溪水環境
            param["dataset"] = "5e6b06a177e80cf258b9ba72" #測試集
        
        #load dataset info & images
        url = config["host"]+"/dataset/view-dataset?id="+param["dataset"]
        r = requests.get(url).json()
        if r["status"] != "ok":
            return {"error":"讀取資料集失敗"}
        dataset = r["data"]
        form = {}
        if "form" in dataset and dataset["form"] != '':
            for formItem in dataset["form"]["itemArr"]:
                key = formItem["id"]
                form[key] = formItem["quest"]
        #print(form)

        url = config["host"]+"/dataset/list-image?all=1&dataset="+param["dataset"]
        r = requests.get(url).json()
        if r["status"] != "ok":
            return {"error":"讀取影像列表失敗"}
        imageArr = r["data"]
        #print(imageArr)

        #generate geojson from data
        geom = {}
        geom["type"] = "FeatureCollection"
        geom["features"] = []
        for image in imageArr:
            if "lat" not in image or "lng" not in image:
                continue
            f = {}
            f["type"] = "Feature"
            f["geometry"] = {
                "type": "Point",
                "coordinates": [image["lng"],image["lat"]]
            }
            f["id"] = image["_id"]
            p = {
                "url":config["host"]+"/image?dataset="+param["dataset"]+"&image="+image["_id"],
                "photo":config["host"]+"/static/upload/dataset/"+param["dataset"]+"/image/"+image["_id"]+".jpg"
            }
            if "remark" in image:
                p["remark"] = image["remark"]
            if image["formReply"] is not None:
                for key in image["formReply"]:
                    if not key in form:
                        continue
                    value = image["formReply"][key]["value"]
                    name = form[key]
                    p[name] = value
            f["properties"] = p
            geom["features"] .append(f)
        #print(geom)

        #generate json_def
        data = {
            "geom": geom,
            "layer": SymbolStyle("camera",textKey="思源地圖名稱",allowOverlap=True),
        }
        if "format" in param and param["format"] == "geojson":
            return geom
        return {
            "layerName": "群眾標註",
            "data": [data]
        }

    def ListCommutagDataset(self,config,param):
        hasMore = True
        page = 0
        dataset = []
        while hasMore:
            url = config["host"]+("/dataset/list-dataset?page=%d&sort=createdAt&orderType=desc") % (page)
            r = requests.get(url).json()
            if r["status"] != "ok":
                return {"error":"讀取資料集列表失敗"}
            result = r["data"]
            hasMore = result["hasMore"]
            #dataset = dataset + result["dataset"]
            for d in result["dataset"]:
                if not "form" in d:
                    continue
                if not isinstance(d["form"], dict):
                    continue
                if not "itemArr" in d["form"]:
                    continue
                hasKind = False
                hasName = False
                for item in d["form"]["itemArr"]:
                    if item["quest"].startswith("思源地圖類別"):
                        hasKind = True
                    if item["quest"].startswith("思源地圖名稱"):
                        hasName = True
                if hasKind and hasName:
                    dataset.append({
                        "_id": d["_id"],
                        "name":d["name"]
                    })
            page += 1
        return dataset
