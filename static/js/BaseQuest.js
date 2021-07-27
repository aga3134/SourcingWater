
class BaseQuest{
    constructor(param){
        this.map = param.map;
        this.quest = param.quest;
        this.sourceHash = {};
        this.layerHash = {};
    }

    Init(){
        this.LoadData();
        this.LoadChart();
    }

    LoadData(callback){
        var url = this.quest.geomUrl;
        $.get(url, (result) => {
            console.log(result);
            for(let i=0;i<result.length;i++){
                var data = result[i];
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
            }
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