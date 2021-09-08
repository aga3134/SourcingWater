class WMTSLayer extends BaseLayer{
    constructor(param){
        super(param);
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
        });
        var visible = this.show?"visible":"none";
        this.map.setLayoutProperty(sourceKey,"visibility",visible);
        this.sourceHash[sourceKey] = {"name":sourceKey};
        this.layerHash[sourceKey] = {"name":sourceKey};
        if(succFn) succFn();
    }
}