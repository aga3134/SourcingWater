
class BaseQuest{
    constructor(param){
        this.map = param.map;
        this.quest = param.quest;
        this.nodeID = null;
        this.nodeName = "";
        this.setting = {};
        this.sourceHash = {};
        this.layerHash = {};
        this.bbox = null;
    }

    Init(callback){
        let promiseArr = [];
        promiseArr.push(new Promise((resolve,reject) => {
            this.LoadData(resolve);
        }));
        promiseArr.push(new Promise((resolve,reject) => {
            this.LoadChart(resolve);
        }));
        Promise.all(promiseArr).then(() => {
            if(callback) callback();
        });
    }

    LoadData(callback){
        var url = this.quest.geomUrl;
        $.get(url, (result) => {
            //console.log(result);
            this.bbox = null;
            if(result.data){
                for(let i=0;i<result.data.length;i++){
                    let data = result.data[i];
                    data.geom = JSON.parse(data.geom);
                    let key = this.GetGeomKey(i);
                    //console.log(key);
                    this.map.addSource(key, {
                        "type": "geojson",
                        "data": data.geom
                    });
                    this.map.addLayer({
                        "id": key,
                        "type": data.type,
                        "source": key,
                        "paint": data.paint
                    });
                    this.sourceHash[key] = {"name":key, "data":data.geom};
                    this.layerHash[key] = {"name":key};
    
                    let bbox = turf.bbox(data.geom);
                    if(!this.bbox){
                        this.bbox = bbox;
                    }
                    else{
                        if(bbox[0] < this.bbox[0]) this.bbox[0] = bbox[0];
                        if(bbox[1] < this.bbox[1]) this.bbox[1] = bbox[1];
                        if(bbox[2] > this.bbox[2]) this.bbox[2] = bbox[2];
                        if(bbox[3] > this.bbox[3]) this.bbox[3] = bbox[3];
                    }
                }
            }
            this.nodeID = result.nodeID;        //用來取資料庫資料
            this.nodeName = result.nodeName;    //用來顯示
            this.setting = result.setting;      //不同display_class會有不同的setting
            
            if(callback) callback();
        });
    }

    ClearAll(){
        //clear data
        for(let key in this.layerHash){
            this.map.removeLayer(this.layerHash[key].name);
        }
        this.layerHash = {};

        for(let key in this.sourceHash){
            this.map.removeSource(this.sourceHash[key].name);
        }
        this.sourceHash = {};
    }

    LoadChart(callback){
        if(callback) callback();
    }

    GetGeomKey(index){
        function ToHash(str){
            let hash = 0, i, chr;
            if (str.length === 0) return hash;
            for (i = 0; i < str.length; i++) {
                chr   = str.charCodeAt(i);
                hash  = ((hash << 5) - hash) + chr;
                hash |= 0; // Convert to 32bit integer
            }
            return hash;
        }
        return ToHash(this.quest.name)+"_"+index;
    }

}

//讓g_APP可以從config字串new出需要的class，後續繼承的子類別也需要把它們的名字註冊到此變數
g_QuestClass = {"BaseQuest": BaseQuest};