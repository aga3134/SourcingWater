
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
                let layer = config.layer[0];
                let option = {
                    "id": key,
                    "type": layer.type,
                    "source": key,
                }
                if("paint" in layer) option.paint = layer.paint;
                if("layout" in layer) option.layout = layer.layout;
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
                            this.DrawPointMove(e.lngLat.lat, e.lngLat.lng);
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
            toastr.info("請再點選"+(config.num-this.shapeData.ptArr.length)+"點");
        }
    }

    DrawPointMove(lat,lng){
        let config = this.setting.shapeConfig;

        let key = this.GetShapeKey();
        let source = this.map.getSource(key);
        if(source){
            let featArr = [];
            if(this.shapeData.ptArr){
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
            }
            featArr.push({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lng,lat]
                }
            });
            source.setData({
                "type": "FeatureCollection",
                "features": featArr
            });
        }
    }

    GetCircleRadius(pt1,pt2){
        let config = this.setting.shapeConfig;
        let radius = turf.distance(
            turf.point(pt1),
            turf.point(pt2)
        )*1000;
        if(config.minR && radius < config.minR) radius = config.minR;
        if(config.maxR && radius > config.maxR) radius = config.maxR;
        return radius;
    }

    DrawCircle(lat,lng){
        let config = this.setting.shapeConfig;
        if(config.fixedRadius){
            this.shapeData.center = [lng,lat];
            this.shapeData.radius = config.fixedRadius;
            this.ConfirmShape();
        }
        else{
            if(!this.shapeData.center){
                this.shapeData.center = [lng,lat];
                this.shapeData.radius = config.minR||0;
            }
            else{
                this.shapeData.radius = this.GetCircleRadius(this.shapeData.center,[lng,lat]);
                this.ConfirmShape();
            }
        }
    }
    DrawCircleMove(lat,lng){
        let config = this.setting.shapeConfig;
        let center = null;
        let radius = 0;
        if(config.fixedRadius){
            center = [lng,lat];
            radius = config.fixedRadius;
        }
        else{
            if(!this.shapeData.center) return;
            else{
                center = this.shapeData.center;
                radius = this.GetCircleRadius(this.shapeData.center,[lng,lat]);
            }
        }
        let options = {steps:64, units:"meters"};
        var circleGeom = turf.circle(center, radius, options);

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

    ClearAll(){
        this.ClearShape();
        super.ClearAll();
    }

    Stop(){
        this.ClearShape();
    }
}

//需把它們的名字註冊到此變數，讓g_APP可以從config字串new出此類別
g_QuestClass["DrawShapeQuest"] = DrawShapeQuest;