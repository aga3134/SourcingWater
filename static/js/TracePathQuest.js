
class TracePathQuest extends BaseQuest{
    constructor(param){
        super(param);
        this.originPath = [];
        this.displayPath = [];
        this.displayIndex = 0;
        this.timer = null;
        this.zoomToBBox = false;
        this.targetQuest = null;
        this.minIndex = 0;
        this.maxIndex = 0;
        this.icon = {
            size: 100,
            outerColor: [255,200,200],
            innerColor: [255,100,100],
            duration: 1000
        }
        this.speed = 0.0003;
        this.step = 0;
    }

    AddFrontendIcon(){
        let map = this.map;
        let icon = this.icon;
        
        if(!this.map.hasImage("pulsing-dot")){
            //using StyleImageIterface to generate icon dynamically
            const pulsingDot = {
                width: icon.size,
                height: icon.size,
                data: new Uint8Array(icon.size*icon.size*4),
    
                onAdd: function () {
                    const canvas = document.createElement('canvas');
                    canvas.width = this.width;
                    canvas.height = this.height;
                    this.context = canvas.getContext('2d');
                },
                    
                render: function () {
                    const t = (performance.now() % icon.duration) / icon.duration;                
                    const radius = (icon.size*0.5)*0.3;
                    const outerRadius = (icon.size*0.5)*0.7*t+radius;
                    const context = this.context;
                    
                    // Draw the outer circle.
                    context.clearRect(0, 0, this.width, this.height);
                    context.beginPath();
                    context.arc(this.width*0.5,this.height*0.5,outerRadius,0,Math.PI*2);
                    context.fillStyle = `rgba(${icon.outerColor[0]},${icon.outerColor[1]},${icon.outerColor[2]},${1-t})`;
                    context.fill();
                    
                    // Draw the inner circle.
                    context.beginPath();
                    context.arc(this.width*0.5,this.height*0.5,radius,0,Math.PI*2);
                    context.fillStyle = `rgba(${icon.innerColor[0]},${icon.innerColor[1]},${icon.innerColor[2]},1)`;
                    context.strokeStyle = 'white';
                    context.lineWidth = 2+4*(1-t);
                    context.fill();
                    context.stroke();
                    
                    this.data = context.getImageData(0,0,this.width,this.height).data;
                    map.triggerRepaint();
                    return true;
                }
            };
            this.map.addImage('pulsing-dot', pulsingDot, {pixelRatio: 2});
        }
        
        let dotKey = this.GetGeomKey(0)+"_dot";
        let source = this.map.getSource(dotKey);
        if(!source){
            this.map.addSource(dotKey, {
                'type': 'geojson',
                'data': null
            });
        }
        let layer = this.map.getLayer(dotKey);
        if(!layer){
            this.map.addLayer({
                'id': dotKey,
                'type': 'symbol',
                'source': dotKey,
                'layout': {
                    'icon-image': 'pulsing-dot'
                }
            });
        }
    }

    Init(succFn,failFn){
        super.Init((result) => {
            this.AddFrontendIcon();
            //?????????quest???????????????????????????quest??????targetQuest???????????????????????????????????????history
            if(g_APP.history.index < 0 || g_APP.history.index >= g_APP.history.questArr.length){
                return toastr.error("???????????????");
            }
            let q = g_APP.history.questArr[g_APP.history.index].quest;
            if(q.targetQuest){
                this.targetQuest = q.targetQuest;
                this.updateHistory = false;
            }
            else this.targetQuest = q;
            
            //????????????????????????????????????????????????UpdateQuestHistory????????????????????????player??????stop
            setTimeout(() => {
                g_APP.OpenPlayerPanel();
                g_APP.player.playFn = (event) => {
                    this.Resume();
                };
                g_APP.player.pauseFn = (event) => {
                    this.Pause();
                };
                g_APP.player.stopFn = (event) => {
                    this.Stop();
                };
                this.Play();
            },100);

            if(succFn) succFn(result);
        }, (reason) => {
            if(failFn) failFn(reason);
        });
    }

    ClearAll(){
        this.Stop();
        super.ClearAll();
    }

    ClearPath(){
        if(this.timer){
            window.clearInterval(this.timer);
            this.timer = null;
        }
        this.displayIndex = 0;

        //remove frontend icon
        let dotKey = this.GetGeomKey(0)+"_dot";
        let source = this.map.getSource(dotKey);
        if(source){
            let pt = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': []
                }
            };
            source.setData(pt);
        }

        //remove path
        if(!this.setting) return;
        if(this.displayPath.coordinates){
            this.displayPath.coordinates = [];
            let key = this.GetGeomKey(0);
            source = this.map.getSource(key);
            if(source) source.setData(this.displayPath);
        }
    }

    Play(){
        if(!this.setting) return;
        this.ClearPath();
        let targetKey = this.targetQuest.GetGeomKey(0);
        let source = this.targetQuest.sourceHash[targetKey];
        if(!source){
            return toastr.error("????????????????????????");
        }
        let coord = null;
        this.minIndex = 0;
        this.maxIndex = 0;
        switch(source.data.type){
            case "FeatureCollection":
                this.maxIndex = source.data.features.length-1;
                if(this.setting.pathIndex < this.minIndex) return toastr.error("????????????????????????");
                if(this.setting.pathIndex > this.maxIndex) return toastr.error("????????????????????????");
                let feature = source.data.features[this.setting.pathIndex];
                this.originPath = feature.geometry;
                if(this.originPath.type != "LineString") return toastr.error("??????????????????");
                coord = this.originPath.coordinates[0];
                break;
            case "Feature":
                this.originPath = source.data.geometry;
                if(this.originPath.type != "MultiLineString") return toastr.error("??????????????????");
                coord = this.originPath.coordinates[0][0];
                break;
            default:
                return toastr.error("??????????????????");
        }
        this.displayPath = {"type":"LineString","coordinates":[]};
        this.displayPath.coordinates = [coord];

        let key = this.GetGeomKey(0);
        source = this.map.getSource(key);
        if(source) source.setData(this.displayPath);
        
        this.map.flyTo({"center": coord, "zoom": 14, "pitch":35});
        this.map.once("moveend", function(){
            this.Resume();
        }.bind(this));
    }

    Pause(){
        g_APP.player.isPlay = false;
        if(this.timer){
            window.clearInterval(this.timer);
            this.timer = null;
        }
    }

    Resume(){
        if(this.timer) return;
        if(!this.setting) return;
        g_APP.player.isPlay = true;
        let key = this.GetGeomKey(0);

        let coordArr = null;
        switch(this.originPath.type){
            case "LineString":
                coordArr = this.originPath.coordinates;
                break;
            case "MultiLineString":
                coordArr = this.originPath.coordinates[0];
                break;
        }
        
        this.timer = window.setInterval(function(){
            if(this.displayIndex < coordArr.length){
                let curPt = coordArr[this.displayIndex];
                let nextPt = coordArr[this.displayIndex+1];
                let coord = [];
                if(!nextPt){    //????????????
                    coord = curPt;
                }
                else{
                    let diff = [nextPt[0]-curPt[0],nextPt[1]-curPt[1]];
                    let norm = Math.sqrt(diff[0]*diff[0]+diff[1]*diff[1]);
                    let progress = this.speed*this.step;
                    //console.log([norm,progress,this.step]);
                    if(norm > progress){   //???speed??????????????????
                        coord[0] = curPt[0]+diff[0]*progress/norm;
                        coord[1] = curPt[1]+diff[1]*progress/norm;
                        this.step++;
                    }
                    else{   //?????????????????????
                        coord = nextPt;
                        this.displayIndex++;
                        this.step = 0;
                    }
                }

                this.displayPath.coordinates.push(coord);
                let source = this.map.getSource(key);
                if(source) source.setData(this.displayPath);
                this.map.panTo(coord);
                let dotKey = this.GetGeomKey(0)+"_dot";
                let frontendIcon = this.map.getSource(dotKey);
                let pt = {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': coord
                    }
                };
                if(frontendIcon) frontendIcon.setData(pt);
            }
            else this.Pause();
        }.bind(this), 100);
    }

    Stop(){
        g_APP.player.isPlay = false;
        this.ClearPath();
        this.map.easeTo({pitch: 30});
        g_APP.ClosePlayerPanel();
    }

}

//?????????????????????????????????????????????g_APP?????????config??????new????????????
g_QuestClass["TracePathQuest"] = TracePathQuest;