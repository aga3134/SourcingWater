
class DrawShapeQuest extends BaseQuest{
    constructor(param){
        super(param);
        this.shapeData = {};
        this.shapeSource = {};  //存在地圖上畫出的形狀
        this.shapeLayer = {};   //存在地圖上畫出的形狀
        this.confirmCallback = null;
    }
    GetShapeKey(){
        return this.uuid+"_shape";
    }
    Init(callback){
        this.confirmCallback = callback;
        super.Init((result) => {
            if(result.info){
                toastr.info(result.info);
                let config = this.setting.shapeConfig;

                //add shape layer
                let key = this.GetShapeKey();
                this.map.addSource(key, {
                    "type": "geojson",
                    "data": null
                });
                let option = {
                    "id": key,
                    "type": config.layer.type,
                    "source": key,
                }
                if("paint" in config.layer) option.paint = config.layer.paint;
                if("layout" in config.layer) option.layout = config.layer.layout;
                this.map.addLayer(option);

                g_APP.eventFn.onClick = (e) => {
                    switch(config.type){
                        case "point":
                            this.DrawPoint(e.lngLat.lat, e.lngLat.lng);
                            break;
                        case "circle":
                            this.DrawCircle(e.lngLat.lat, e.lngLat.lng);
                            break;
                        case "polyline":
                            this.DrawPolyline(e.lngLat.lat, e.lngLat.lng);
                            break;
                        case "polygon":
                            this.DrawPolygon(e.lngLat.lat, e.lngLat.lng);
                            break;
                    }
                }
                g_APP.eventFn.onMouseMove = (e) => {
                    switch(config.type){
                        case "point":
                            break;
                        case "circle":
                            this.DrawCircleMove(e.lngLat.lat, e.lngLat.lng);
                            break;
                        case "polyline":
                            this.DrawPolylineMove(e.lngLat.lat, e.lngLat.lng);
                            break;
                        case "polygon":
                            this.DrawPolygonMove(e.lngLat.lat, e.lngLat.lng);
                            break;
                    }
                }
            }
            //取得資料成功才跳轉到下個類別
            else if(callback) callback(result);
        });
    }
    ClearShape(){
        let key = this.GetShapeKey();
        this.map.removeLayer(key);
        this.map.removeSource(key);
    }
    DrawPoint(lat,lng){
        let config = this.setting.shapeConfig;
        if(!this.shapeData.ptArr) this.shapeData.ptArr = [];
        this.shapeData.ptArr.push([lng,lat]);

        let key = this.GetShapeKey();
        let source = this.map.getSource(key);
        if(source){
            let featArr = [];
            for(let i=0;i<this.shapeData.ptArr.length;i++){
                let pt = this.shapeData.ptArr[i];
                featArr.push({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [pt[0],pt[1]]
                    }
                });
            }
            source.setData({
                "type": "FeatureCollection",
                "features": featArr
            });
        }
        if(this.shapeData.ptArr.length >= config.num){
            this.ConfirmShape();
        }
    }

    DrawCircle(lat,lng){
        let config = this.setting.shapeConfig;
    }
    DrawMove(lat,lng){
        let config = this.setting.shapeConfig;
    }

    DrawPolyline(lat,lng){
        let config = this.setting.shapeConfig;
    }
    DrawPolylineMove(lat,lng){
        let config = this.setting.shapeConfig;
    }

    DrawPolygon(lat,lng){
        let config = this.setting.shapeConfig;
    }
    DrawPolygonMove(lat,lng){
        let config = this.setting.shapeConfig;
    }

    ConfirmShape(){
        let config = this.setting.shapeConfig;
        let urlString = this.quest.geomUrl.split("?");
        var params = new URLSearchParams(urlString[1]);
        params.set(config.variable,JSON.stringify(this.shapeData));
        this.quest.geomUrl = urlString[0]+"?"+params.toString();
        //console.log(this.quest.geomUrl);
        this.Init(this.confirmCallback);
        this.ClearShape();
    }
}

//需把它們的名字註冊到此變數，讓g_APP可以從config字串new出此類別
g_QuestClass["DrawShapeQuest"] = DrawShapeQuest;