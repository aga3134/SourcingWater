class LUIMapLayer extends WMTSLayer{
    constructor(param){
        super(param);
        this.mapName = "LUIMAP01";
        this.urlTemplate = "https://wmts.nlsc.gov.tw/wmts/{MapName}/default/GoogleMapsCompatible/{z}/{y}/{x}";
        this.url = this.urlTemplate.replace("{MapName}",this.mapName);
    }
    Update(){
        this.url = this.urlTemplate.replace("{MapName}",this.mapName);
        this.LoadData(this.url);
    }

}