
class BaseLayer{
    constructor(param){
        this.url = param.url;
        this.show = param.show;
        this.map = param.map;
        this.sourceHash = {};
        this.layerHash = {};
        this.bbox = null;
        this.zoomToBBox = true;
        this.updateHistory = false;
        this.uuid = uuidv4();
        this.data = null;
        this.layerName = "";
        this.hoverFeature = null;
        this.hoverSource = null;
        this.inited = false;

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
                let boxSize = 10;
                let f = this.map.queryRenderedFeatures(
                    [[e.point.x - boxSize*0.5, e.point.y - boxSize*0.5],
                    [e.point.x + boxSize*0.5, e.point.y + boxSize*0.5]]
                )[0];
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
                if(this.hoverSource != null && this.hoverFeature != null){
                    this.map.setFeatureState(
                        {source: this.hoverSource, id: this.hoverFeature},
                        {hover: false}
                    );
                    this.hoverSource = null;
                    this.hoverFeature = null;
                }
            };
        }

    }
    
    Init(succFn,failFn){
        let promiseArr = [];
        promiseArr.push(new Promise((resolve,reject) => {
            this.LoadData(this.url,resolve,reject);
        }));
        Promise.all(promiseArr).then((result) => {
            this.inited = true;
            if(succFn) succFn(result);
        }, (reason) => {
            this.inited = false;
            if(failFn) failFn(reason);
        });
    }
    GetGeomKey(index){
        return this.uuid+"_"+index;
    }

    LoadData(url,succFn,failFn){
        this.ClearAll();
        g_APP.isProcessing = true;
        
        $.get(url, (result) => {
            //console.log(result);
            if(result.error){
                toastr.error(result.error);
                if(failFn) failFn(result);
                g_APP.isProcessing = false;
                return;
            }
            if(result.info){
                toastr.info(result.info);
            }
            this.bbox = null;
            if(result.layerName) this.layerName = result.layerName;
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
                    //??????source??????????????????layer???????????????????????????????????????
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
            if(succFn) succFn(result);
            g_APP.isProcessing = false;
        });
    }

    Update(){
        let UpdateLayer = () => {
            let visible = this.show?"visible":"none";
            for(let key in this.layerHash){
                let layer = this.layerHash[key].name;
                this.map.setLayoutProperty(layer,"visibility",visible);
            }
        }

        if(!this.inited){
            this.Init(UpdateLayer);
        }
        else UpdateLayer();
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
