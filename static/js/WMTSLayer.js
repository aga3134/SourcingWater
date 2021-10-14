class WMTSLayer extends BaseLayer{
    constructor(param){
        super(param);
        this.urlTemplate = param.urlTemplate;
        this.urlVariable = param.urlVariable;
        this.url = this.GetUrl();
    }
    GetUrl(){
        let url = this.urlTemplate;
        for(let key in this.urlVariable){
            url = url.replace("{"+key+"}",this.urlVariable[key]);
        }
        return url;
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
        if(succFn) succFn();
    }

    Update(){
        this.url = this.GetUrl();
        this.LoadData(this.url);
    }
}