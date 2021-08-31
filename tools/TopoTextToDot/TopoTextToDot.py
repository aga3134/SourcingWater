from argparse import ArgumentParser

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-i", help="input filename", dest="inFile")
    parser.add_argument("-o", help="output filename", dest="outFile")
    args = parser.parse_args()

    if args.inFile is None:
        print("Usage: TopoTextToDot.py -i [input_file_name] -o [output_file_name]")
        exit(0)
    if args.outFile is None:
        args.outFile = "output.dot"
		
    with open(args.inFile,"r",encoding="utf8") as f:
        lines = f.readlines()

    with open(args.outFile,"w",encoding="utf8") as f:
        data = "digraph G {\n"
        for line in lines:
            line=line.strip()
            cols=line.split(",")
            #預設:完成
            color="green"
            style = ""
            if cols[3]=="1": #展示
                color="orange"
            elif cols[3]=="2":#沒資料
                color="red"
            elif cols[3]=="3": #待整合
                color="blue" 
            elif cols[3]=="4": #發想中
                color="gray"
            data += "\t\"%s\"->\"%s\"[label=\"%s\",color=\"%s\",style=\"%s\"]\n" %(cols[0],cols[2],cols[1],color,style)

        data += "}\n"
        print(data)
        f.write(data)
