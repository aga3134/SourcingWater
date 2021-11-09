class UavLayer extends BaseLayer{
    constructor(param){
        super(param);
        this.filename = param.filename;
        this.uavOption = [];
        this.uavIndex = 0;
        this.url = "";
        $.get(this.filename, (result) => {
            this.uavOption = result;
            this.uavIndex = 0;
        });
    }

    GetUrl(){
        if(this.uavIndex < 0 || this.uavIndex >= this.uavOption.length) return "";
        else return this.uavOption[this.uavIndex].url;
    }

    LoadData(url,succFn,failFn){
        this.ClearAll();
        let sourceKey = this.GetGeomKey(0);
        this.map.addSource(sourceKey, {
            "type": "raster",
            "tiles": [url]
        });
        this.map.addLayer({
            "id": sourceKey,
            "type": "raster",
            "source": sourceKey,
            "paint": {}
        },g_APP.wmtsBarrier);
        var visible = this.show?"visible":"none";
        this.map.setLayoutProperty(sourceKey,"visibility",visible);
        this.sourceHash[sourceKey] = {"name":sourceKey};
        this.layerHash[sourceKey] = {"name":sourceKey};

        //zoom to bbox
        if(this.show){
            let uav = this.uavOption[this.uavIndex];
            if(uav && uav.bbox){
                this.map.fitBounds([
                    [uav.bbox[0],uav.bbox[1]],
                    [uav.bbox[2],uav.bbox[3]]
                ]);
            }
        }
        
        if(succFn) succFn();
    }

    Update(){
        this.url = this.GetUrl();
        this.LoadData(this.url);
    }
}