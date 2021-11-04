def GenValue(record, keyStr):
    val = ""
    arr = keyStr.split(",")
    
    n = len(arr)
    for i in range(0,n):
        key = arr[i].strip()
        value = record[key]
        #字串
        if isinstance(value,str):
            val+="'"+value+"'"
        elif value is None:
            val+="NULL"
        else:   #數字
            val+=str(value)
        if i < n-1:
            val+=","
    return val

def IsNumber(s):
    if s is None:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False
    
def VarifyValue(value):
    if IsNumber(value):    
        return value
    else:
        return 0
    
def PadLeft(value,ch,digit):
    leftPad = ""
    if len(value) < digit:
        for i in range(digit-len(value)):
            leftPad += ch
    return leftPad + value

def GenDBTuple(record, keyStr):
    formatArr = []
    dbTuple = ()
    arr = keyStr.split(",")
    
    n = len(arr)
    for i in range(0,n):
        key = arr[i].strip()
        value = record[key]
        formatArr.append("%s")
        dbTuple = dbTuple + (value,)
        
    format = ",".join(formatArr)
    return (format,dbTuple)

def DataToDB(engine, table, d):
    field = ",".join(d.keys())
    (format,dbTuple) = GenDBTuple(d,field)
    with engine.connect() as conn:
        sql = "INSERT INTO "+table+" ("+field+") VALUES ("+format+") ON CONFLICT DO NOTHING"
        #try:
        conn.execute(sql,dbTuple)
        #except:
            #print("excute fail: "+sql)