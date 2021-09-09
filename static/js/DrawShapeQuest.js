
class DrawShapeQuest extends BaseQuest{
    constructor(param){
        super(param);
        this.shapeData = {};
        this.shapeSource = null;  //存在地圖上畫出的形狀
        this.shapeLayer = null;   //存在地圖上畫出的形狀
        this.confirmCallback = null;
    }
    GetShapeKey(){
        return this.uuid+"_shape";
    }
    Init(succFn,failFn){
        this.confirmCallback = succFn;
        super.Init((result) => {
            if(result.setting && result.setting.shapeConfig){
                let config = this.setting.shapeConfig;
                //add shape layer
                let key = this.GetShapeKey();
                this.shapeSource = this.map.addSource(key, {
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
                this.shapeLayer = this.map.addLayer(option);

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
            else if(succFn) succFn(result);
        }, (reason) => {
            //reset geomUrl
            if(this.setting.shapeConfig){
                let config = this.setting.shapeConfig;
                let urlString = this.quest.geomUrl.split("?");
                var params = new URLSearchParams(urlString[1]);
                params.delete(config.variable);
                this.quest.geomUrl = urlString[0]+"?"+params.toString();
            }
            if(failFn) failFn();
        });
    }
    ClearShape(){
        let key = this.GetShapeKey();
        if(this.shapeLayer){
            this.map.removeLayer(key);
            this.shapeLayer = null;
        }
        if(this.shapeSource){
            this.map.removeSource(key);
            this.shapeSource = null;
        }
        this.shapeData = {};
    }
    ClearEventFn(){
        g_APP.eventFn.onClick = null;
        g_APP.eventFn.onMouseMove = null;
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
        else{
            toastr.info("請再點選"+config.num-this.shapeData.ptArr.length+"點");
        }
    }

    DrawCircle(lat,lng){
        let config = this.setting.shapeConfig;
        this.shapeData.center = [lng,lat];
        this.shapeData.radius = 1000;
        this.ConfirmShape();
    }
    DrawCircleMove(lat,lng){
        let config = this.setting.shapeConfig;
        let options = {steps:64, units:"meters"};
        let center = [lng,lat]; 
        var circleGeom = turf.circle(center, 1000, options);

        let key = this.GetShapeKey();
        let source = this.map.getSource(key);
        if(source){
            source.setData(circleGeom);
        }
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
        this.ClearEventFn();
    }
}

//需把它們的名字註冊到此變數，讓g_APP可以從config字串new出此類別
g_QuestClass["DrawShapeQuest"] = DrawShapeQuest;