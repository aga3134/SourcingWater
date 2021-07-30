let g_APP = new Vue({
    el: "#app",
    data: {
        map: null,
        openOptionPanel: false,
        openQuestPanel: false,
        openChartPanel: false,
        openAboutPanel: false,
        openPlayerPanel: false,
        logicTopo:{
            kind:{},
            transfer:{},
            curKind:"",
            nodeID:""
        },
        questArr: [],
        curQuest: {
            index: -1,
            quest: null,
        },
        player:{
            isPlay: false,
            playFn: "",
            pauseFn: "",
            stopFn: ""
        },
        layer:{
            basin: null
        }
    },
    delimiters: ['[[',']]'],    //vue跟jinja的語法會衝突
    created: function(){
        window.addEventListener('load', () => {
            let promiseArr = [];
            promiseArr.push(new Promise((resolve,reject) => {
                this.InitMap(resolve);
            }));
            promiseArr.push(new Promise((resolve,reject) => {
                $.get("logicTopo/kind", (result) => {
                    this.logicTopo.kind = {};
                    for(let i=0;i<result.length;i++){
                        let r = result[i];
                        this.logicTopo.kind[r.kind] = r;
                    }
                    //console.log(this.logicTopo.kind);
                    resolve();
                });
            }));
            promiseArr.push(new Promise((resolve,reject) => {
                $.get("logicTopo/transfer", (result) => {
                    this.logicTopo.transfer = {};
                    for(let i=0;i<result.length;i++){
                        let r = result[i];
                        let kind = r["from_類別"];
                        if(!(kind in this.logicTopo.transfer)) this.logicTopo.transfer[kind] = [];
                        this.logicTopo.transfer[kind].push(r);
                    }
                    //console.log(this.logicTopo.transfer);
                    resolve();
                });
            }));
            promiseArr.push(new Promise((resolve,reject) => {
                let param = {
                    show: false,
                    map: this.map,
                    url: "layer/basin",
                    onClick: (e) => {
                        let f = e.features[0];
                        if(!f) return;
                        this.logicTopo.curKind = "流域";
                        this.logicTopo.nodeID = f.properties.basin_name;
                        this.LoadQuest();
                        this.SelectQuest(0);
                        this.layer.basin.show = false;
                        this.UpdateLayer();
                    },
                };
                this.layer.basin = new BaseLayer(param);
                this.layer.basin.Init(resolve);
            }));
            Promise.all(promiseArr).then(() => {
                this.logicTopo.curKind = "流域";
                this.logicTopo.nodeID = "頭前溪";
                this.LoadQuest();
                this.SelectQuest(0);
            });
            
        });
    },
    methods:{
        InitMap: function(callback){
            let accessToken = $("meta[name='accessToken']").attr("content");
            mapboxgl.accessToken = accessToken;
            this.map = new mapboxgl.Map({
                container: 'map',
                style: 'mapbox://styles/aga3134/ckpqd8kxb0pph17px4usqsea5',
                center: [121, 23.7],
                zoom: 6.5
            });
            
            this.map.on('load', function(){
                this.map.addSource('mapbox-dem', {
                    'type': 'raster-dem',
                    'url': 'mapbox://mapbox.mapbox-terrain-dem-v1',
                    'tileSize': 512,
                    'maxzoom': 13
                });
                this.map.setTerrain({ 'source': 'mapbox-dem', 'exaggeration': 1.5 });
                this.map.addLayer({
                    'id': 'sky',
                    'type': 'sky',
                    'paint': {
                        'sky-type': 'atmosphere',
                        'sky-atmosphere-sun': [0.0, 0.0],
                        'sky-atmosphere-sun-intensity': 15
                    }
                });
                
                //add search box
                let geocoder = new MapboxGeocoder({
                    accessToken: mapboxgl.accessToken,
                    placeholder: "搜尋地點",
                    mapboxgl: mapboxgl
                });
                document.getElementById('geocoder').appendChild(geocoder.onAdd(this.map));

                if(callback) callback();
            }.bind(this));

            this.map.on('click', function(e) {
                console.log(e);
                let url = "logicTopo/findNodeByKind?kind=地點";
                url += "&lat="+e.lngLat.lat;
                url += "&lng="+e.lngLat.lng;
                this.questArr = [{
                    "name": "位於哪個里",
                    "class":"BaseQuest",
                    "geomUrl": url,
                    "targetKind": "地點"
                }];
                this.SelectQuest(0);
            }.bind(this));
        },
        LoadQuest: function(){
            let transfer = this.logicTopo.transfer[this.logicTopo.curKind];
            //console.log(transfer);
            this.questArr = [];
            for(let i=0;i<transfer.length;i++){
                let t = transfer[i];
                let geomUrl = "logicTopo/findNodeByTransfer";
                geomUrl += "?kind="+t["from_類別"];
                geomUrl += "&transfer="+t["類別情境與問題"];
                geomUrl += "&nodeID="+this.logicTopo.nodeID;
                this.questArr.push({
                    "name": t["類別情境與問題"],
                    "class":t["quest_class"]?t["quest_class"]:"BaseQuest",
                    "geomUrl": geomUrl,
                    "chartUrl":"",
                    "targetKind": t["to_類別"]
                });
            }
        },
        ZoomToBBox: function(bbox){
            if(bbox){
                this.map.fitBounds([
                    [bbox[0],bbox[1]],
                    [bbox[2],bbox[3]]
                ]);
            }
        },
        ShowAllBasin: function(){
            if(!this.layer.basin) return;
            this.ClearQuest();
            this.layer.basin.show = true;
            this.UpdateLayer();
            this.ZoomToBBox(this.layer.basin.bbox);
        },
        UpdateLayer: function(){
            if(this.layer.basin) this.layer.basin.Update();
        },
        SetMapPadding: function(padding){
            this.map.easeTo({padding: padding, duration: 1000});
        },
        OpenOptionPanel: function(){
            this.openOptionPanel = true;
            this.SetMapPadding({left: $(".left-panel").width()});
        },
        CloseOptionPanel: function(){
            this.openOptionPanel = false;
            this.SetMapPadding({left:0});
        },
        OpenQuestPanel: function(){
            this.openQuestPanel = true;
            this.SetMapPadding({right: $(".right-panel").width()});
        },
        CloseQuestPanel: function(){
            this.openQuestPanel = false;
            this.SetMapPadding({right:0});
        },
        OpenChartPanel: function(){
            this.openChartPanel = true;
            this.SetMapPadding({bottom: $(".bottom-panel").height()});
        },
        CloseChartPanel: function(){
            this.openChartPanel = false;
            this.SetMapPadding({bottom:0});
        },
        OpenAboutPanel: function(){
            this.openAboutPanel = true;
        },
        CloseAboutPanel: function(){
            this.openAboutPanel = false;
        },
        OpenPlayerPanel: function(){
            this.openPlayerPanel = true;
        },
        ClosePlayerPanel: function(){
            this.openPlayerPanel = false;
        },
        ClearQuest: function(){
            if(this.curQuest.quest){
                this.curQuest.quest.ClearAll();
                this.curQuest.quest = null;
            }
            this.curQuest.index = -1;
        },
        SelectQuest: function(i){
            this.ClearQuest();

            this.curQuest.index = i;
            let quest = this.questArr[i];
            let param = {
                "map": this.map,
                "quest": quest
            };
            this.curQuest.quest = new g_QuestClass[quest.class](param);
            this.curQuest.quest.Init(() => {
                this.logicTopo.curKind = quest.targetKind;
                this.logicTopo.nodeID = this.curQuest.quest.nodeID;
                this.ZoomToBBox(this.curQuest.quest.bbox);
                this.LoadQuest();
            });
            
        },
        TracePath: function(param){
            let key = this.ToHash(this.curQuest.name)+"_"+param.index;
            
            let ClearTimer = function(){
                window.clearInterval(this.tracePath.timer);
                this.tracePath.timer = null;
                this.tracePath.displayPath.coordinates[0] = [];
                this.map.getSource(key).setData(this.tracePath.displayPath);
                this.map.easeTo({pitch: 30});
            }.bind(this);

            if(this.tracePath.timer){
                ClearTimer();
            }
            else{
                let source = this.curQuest.source[key];
                this.tracePath.originPath = source.data;
                this.tracePath.displayPath = $.extend(true, {}, source.data);
                let coord = this.tracePath.originPath.coordinates[0];
                this.tracePath.displayPath.coordinates[0] = [coord[0]];
                this.tracePath.curIndex = 0;
                source = this.map.getSource(key);
                if(source) source.setData(this.tracePath.displayPath);
                
                this.map.flyTo({"center": coord[0], "zoom": 14, "pitch":35});
                this.map.once("moveend", function(){
                    this.tracePath.timer = window.setInterval(function(){
                        if(this.tracePath.curIndex < coord.length){
                            this.tracePath.displayPath.coordinates[0].push(coord[this.tracePath.curIndex]);
                            let source = this.map.getSource(key);
                            if(source) source.setData(this.tracePath.displayPath);
                            this.map.panTo(coord[this.tracePath.curIndex]);
                            this.tracePath.curIndex++;
                        }
                        else ClearTimer();
                    }.bind(this), 100);
                }.bind(this));
            }
        },
    }
});