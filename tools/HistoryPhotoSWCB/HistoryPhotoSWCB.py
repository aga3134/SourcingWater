from argparse import ArgumentParser
from sqlalchemy import create_engine
import json
import os
import requests
from util import *

if __name__ == "__main__":
    with open("../../config.json","r") as json_file:
        data = json_file.read()
        config = json.loads(data)
        pg = config["postgres"]
        engine = create_engine("postgresql+psycopg2://%s:%s@%s:%s/%s" % (pg["user"],pg["password"],pg["host"],pg["port"],pg["db"]))
        
        with engine.connect() as conn:
            sql = """CREATE TABLE if not exists history_photo_swcb (
                eventid varchar(32),
                phototype varchar(8),
                lat float,
                lng float,
                county varchar(32),
                town varchar(32),
                vill varchar(32),
                photodate date,
                photoangle float,
                source varchar(128),
                landmark varchar(128),
                description varchar(1024),
                note varchar(256),
                pagephoto varchar(32),
                disasteryear int,
                disastername varchar(128),
                filename varchar(256),
                geom geometry,
                PRIMARY KEY (eventid)
            )"""
            conn.execute(sql)

            #load data from url
            page = 0
            while True:
                url = "https://photo.swcb.gov.tw/api/media/0/List?page="+str(page)
                print("fetch "+url)
                r = requests.get(url)
                r.encoding = "utf-8"
                if r.status_code == requests.codes.all_okay:
                    data = r.json()
                    if len(data) == 0:
                        break
                    #print(data)
                    for d in data:
                        if d["Lat"] == 0 and d["Lng"] == 0:
                            continue
                        d["geom"] = "POINT(%f %f)" % (d["Lng"],d["Lat"])
                        #print(d)
                        DataToDB(engine,"history_photo_swcb",d)
            
                page +=1