
class BaseLayer{
    constructor(param){
        this.url = param.url;
        this.show = param.show;
        this.map = param.map;
        this.sourceHash = {};
        this.layerHash = {};
        this.bbox = null;
        this.uuid = uuidv4();
    }
    
    Init(callback){
        let promiseArr = [];
        promiseArr.push(new Promise((resolve,reject) => {
            this.LoadData(this.url,resolve);
        }));
        Promise.all(promiseArr).then((values) => {
            if(callback) callback(values);
        });
    }
    GetGeomKey(index){
        return this.uuid+"_"+index;
    }

    LoadData(url,callback){
        this.ClearAll();
        
        $.get(url, (result) => {
            this.bbox = null;
            if(result.data){
                var visible = this.show?"visible":"none";
                for(let i=0;i<result.data.length;i++){
                    let data = result.data[i];
                    data.geom = JSON.parse(data.geom);
                    let sourceKey = this.GetGeomKey(i);
                    //console.log(sourceKey);
                    this.map.addSource(sourceKey, {
                        "type": "geojson",
                        "data": data.geom
                    });
                    this.sourceHash[sourceKey] = {"name":sourceKey, "data":data.geom};
                    //一個source可以產生多個layer，如一個畫外框，一個畫填滿
                    for(let j=0;j<data.style.length;j++){
                        let s = data.style[j];
                        let layerKey = sourceKey+"_"+j;
                        this.map.addLayer({
                            "id": layerKey,
                            "type": s.type,
                            "source": sourceKey,
                            "paint": s.paint
                        });
                        this.layerHash[layerKey] = {"name":layerKey};
                        this.map.setLayoutProperty(layerKey,"visibility",visible);
                    }
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
            if(callback) callback(result);
        });
    }

    Update(){
        var visible = this.show?"visible":"none";
        for(let key in this.layerHash){
            var layer = this.layerHash[key].name;
            this.map.setLayoutProperty(layer,"visibility",visible);
        }
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

}
