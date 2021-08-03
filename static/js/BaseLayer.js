
class BaseLayer{
    constructor(param){
        this.url = param.url;
        this.show = param.show;
        this.map = param.map;
        this.sourceHash = {};
        this.layerHash = {};
        this.bbox = null;
        this.zoomToBBox = true;
        this.uuid = uuidv4();
        this.data = null;
        this.layerName = "";
        this.hoverFeature = null;
        this.hoverSource = null;

        this.onMouseEnter = param.onMouseEnter;
        this.onMouseMove = param.onMouseMove;
        this.onMouseLeave = param.onMouseLeave;
        this.onClick = param.onClick;
        //add default mouse functions if not provided
        if(!this.onMouseMove){
            this.onMouseMove = (e) => {
                if(this.hoverSource != null && this.hoverFeature != null){
                    this.map.setFeatureState(
                        {source: this.hoverSource, id: this.hoverFeature},
                        {hover: false}
                    );
                    this.hoverSource = null;
                    this.hoverFeature = null;
                }
                let f = this.map.queryRenderedFeatures(e.point)[0];
                if(!f) return;
                this.hoverSource = f.source;
                this.hoverFeature = f.id;
                if(this.hoverSource != null && this.hoverFeature != null){
                    this.map.setFeatureState(
                        {source: f.source, id: f.id},
                        {hover: true}
                    );
                }
            };
        }
        if(!this.onMouseLeave){
            this.onMouseLeave = (e) => {
                let f = this.map.queryRenderedFeatures(e.point)[0];
                if(!f) return;
                if(f.source != null && f.id != null){
                    this.map.setFeatureState(
                        {source: f.source, id: f.id},
                        {hover: false}
                    );
                }
            };
        }

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
            if(result.error){
                return toastr.error(result.error);
            }
            this.bbox = null;
            if(result.layerName) this.layerName = result.layerName;
            //console.log(result);
            if(result.data){
                this.data = result.data;
                var visible = this.show?"visible":"none";
                for(let i=0;i<result.data.length;i++){
                    let data = result.data[i];
                    //data.geom = JSON.parse(data.geom);
                    let sourceKey = this.GetGeomKey(i);
                    //console.log(sourceKey);
                    this.map.addSource(sourceKey, {
                        "type": "geojson",
                        "data": data.geom
                    });
                    this.sourceHash[sourceKey] = {"name":sourceKey, "data":data.geom};
                    //一個source可以產生多個layer，如一個畫外框，一個畫填滿
                    for(let j=0;j<data.layer.length;j++){
                        let s = data.layer[j];
                        let layerKey = sourceKey+"_"+j;
                        let option = {
                            "id": layerKey,
                            "type": s.type,
                            "source": sourceKey,
                        }
                        if("paint" in s) option.paint = s.paint;
                        if("layout" in s) option.layout = s.layout;
                        this.map.addLayer(option);
                        this.layerHash[layerKey] = {"name":layerKey};
                        this.map.setLayoutProperty(layerKey,"visibility",visible);

                        this.map.on("mouseenter", layerKey, (e) => {
                            if(this.onMouseEnter) this.onMouseEnter(e);
                        });

                        this.map.on("mousemove", layerKey, (e) => {
                            if(this.onMouseMove) this.onMouseMove(e);
                        });

                        this.map.on("mouseleave", layerKey, (e) => {
                            if(this.onMouseLeave) this.onMouseLeave(e);
                        });

                        this.map.on("click", layerKey, (e) => {
                            if(this.onClick) this.onClick(e);
                        });
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
