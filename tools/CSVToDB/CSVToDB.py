import subprocess
from argparse import ArgumentParser
from sqlalchemy import create_engine
import json
import os
import pandas as pd

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-i", help="input filename", dest="inFile")
    parser.add_argument("-t", help="table name", dest="table")
    parser.add_argument("--drop", help="drop table or not", dest="drop", default=False,action="store_true")
    args = parser.parse_args()

    if args.inFile is None or args.table is None:
        print("Usage: CSVToDB.py -i [input_file_name] -t [table_name]")
        exit(0)

    with open("../../config.json","r") as json_file:
        data = json_file.read()
        config = json.loads(data)
        pg = config["postgres"]
        engine = create_engine("postgresql+psycopg2://%s:%s@%s:%s/%s" % (pg["user"],pg["password"],pg["host"],pg["port"],pg["db"]))
        
        #copy csv to table
        df = pd.read_csv(args.inFile)
        df.to_sql(args.table, engine, if_exists= 'replace', index= False)

        #check result table
        conn = engine.connect()
        sql = "select * from %s" % args.table
        rows = conn.execute(sql)
        for row in rows:
            print(row)
        
        conn.close()
    