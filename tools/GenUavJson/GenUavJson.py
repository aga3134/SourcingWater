
from argparse import ArgumentParser
import json
import os
import pandas as pd

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-i", help="input filename", dest="inFile")
    parser.add_argument("-o", help="output filename", dest="outFile")
    args = parser.parse_args()

    if args.inFile is None:
        print("Usage: GenUavJson.py -i [input_file_name] -o [output_file_name]")
        exit(0)
    if args.outFile is None:
        args.outFile = "uav.json"

    df = pd.read_csv(args.inFile)
    size,_ = df.shape
    result = []
    for i in range(size):
        d = {}
        minLat = df["WGS84_Y_min"][i]
        maxLat = df["WGS84_Y_max"][i]
        minLng = df["WGS84_X_min"][i]
        maxLng = df["WGS84_X_max"][i]
        d["url"] = df["QGIS使用XYZ連線新增的網址"][i]
        d["name"] = df["UAV拍攝日與位置"][i]
        d["bbox"] = [minLng,minLat,maxLng,maxLat]
        result.append(d)

    print("output data to "+args.outFile)
    with open(args.outFile,'w') as outFile:
        json.dump(result, outFile)
    