let g_APP = new Vue({
    el: "#app",
    data: {
        map: null,
        isLoading: true,
        openOptionPanel: false,
        openQuestPanel: false,
        openChartPanel: false,
        openAboutPanel: false,
        openPlayerPanel: false,
        openQuestInputPanel: false,
        logicTopo:{
            kind:{},
            transfer:{},
            curKind:"",
            nodeID:"",
            nodeName:""
        },
        questArr: [],
        curQuest: {
            index: -1,
            quest: null,
        },
        history:{
            maxSize:  5,
            questArr:[],
            index:-1
        },
        player:{
            isPlay: false,
            playFn: "",
            pauseFn: "",
            stopFn: ""
        },
        questInput:{
            config:[],
            updateFn:""
        },
        layer:{
            basin: null,
            rainStation: null,
            floodStation: null,
            LUIMap: null,
            commutag: null
        },
        eventFn:{
            onMouseMove: null,
            onClick:null
        },
        curBasin:"",
        chartArr:[],
        infoWindow: null
    },
    delimiters: ['[[',']]'],    //vue跟jinja的語法會衝突
    created: function(){
        window.addEventListener('load', () => {
            let promiseArr = [];
            promiseArr.push(new Promise((resolve,reject) => {
                this.InitMap(resolve);
            }));
            //load logic topology
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
            //add icon images
            let iconArr = [
                {name:"flood-station",url:"static/image/alert-24.png"},
                {name:"rain-station",url:"static/image/water-24.png"},
                {name:"marker-red",url:"static/image/marker-red-24.png"},
                {name:"marker-blue",url:"static/image/marker-blue-24.png"},
                {name:"waterin",url:"static/image/waterin-24.png"},
                {name:"waterwork",url:"static/image/waterwork-24.png"},
                {name:"camera",url:"static/image/camera-24.png"},
            ];
            for(let i=0;i<iconArr.length;i++){
                let icon = iconArr[i];
                promiseArr.push(new Promise((resolve,reject) => {
                    this.map.loadImage(icon.url,(error,image) => {
                        this.map.addImage(icon.name, image);
                        resolve();
                    });
                }));
            }
            Promise.all(promiseArr).then(() => {
                //load option layers
                promiseArr.push(new Promise((resolve,reject) => {
                    let param = {
                        show: false,
                        map: this.map,
                        url: "layer/basin",
                        onClick: (e) => {
                            let f = e.features[0];
                            if(!f) return;
                            this.SelectBasin(f.properties.basin_no);
                        },
                    };
                    this.layer.basin = new BaseLayer(param);
                    this.layer.basin.Init(resolve);
                }));
                promiseArr.push(new Promise((resolve,reject) => {
                    let param = {
                        show: false,
                        map: this.map,
                        url: "layer/rainStation",
                    };
                    this.layer.rainStation = new BaseLayer(param);
                    resolve();
                }));
                promiseArr.push(new Promise((resolve,reject) => {
                    let param = {
                        show: false,
                        map: this.map,
                        url: "layer/floodStation",
                    };
                    this.layer.floodStation = new BaseLayer(param);
                    resolve();
                }));
                promiseArr.push(new Promise((resolve,reject) => {
                    let param = {
                        show: false,
                        map: this.map,
                        url: "layer/commutag?dataset=60c0307db652fe1483444844",
                        onClick: (e) => {
                            let f = e.features[0];
                            if(!f) return;
                            let pt = f.geometry.coordinates;
                            let content = "<div class='commutag'>";
                            content += "<a href='"+f.properties.url+"' target='_blank'>";
                            content += "<img class='photo' src='"+f.properties.photo+"'>";
                            content += "</a>";
                            if(f.properties["名稱"]){
                                content += "<div class='title'>"+f.properties["名稱"]+"</div>";
                            }
                            if(f.properties.remark){
                                content += "<div>"+f.properties.remark+"</div>";
                            }
                            
                            if(this.infoWindow){
                                this.infoWindow.remove();
                            }
                            this.infoWindow = new mapboxgl.Popup({
                                closeOnClick: false,
                                maxWidth:"100%"
                            })
                            .setLngLat([pt[0], pt[1]])
                            .setHTML(content)
                            .addTo(this.map);

                            if(f.properties["類別"] && f.properties["名稱"]){
                                this.logicTopo.curKind = f.properties["類別"];
                                this.logicTopo.nodeID = f.properties["名稱"];
                                this.logicTopo.nodeName = f.properties["名稱"];
                                this.LoadQuest();
                                this.curQuest.index = -1;
                            }
                        }
                    };
                    this.layer.commutag = new BaseLayer(param);
                    resolve();
                }));
                
                Promise.all(promiseArr).then(() => {
                    this.SelectBasin("1300");   //頭前溪
                    this.OpenQuestPanel();
                });
            });
        });
        toastr.options = {
            "positionClass":"toast-top-center",
            "showDuration": 300,
            "hideDuration": 300,
            "timeOut": 3000
        };
        this.isLoading = false;
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

                //國土利用圖層
                this.layer.LUIMap = new LUIMapLayer({map:this.map,show:false});
                this.layer.LUIMap.Init();

                if(callback) callback();
            }.bind(this));

            this.map.on('click', function(e) {
                if(this.eventFn.onClick) return this.eventFn.onClick(e);

                //預設點地圖若沒點到東西，就用座標取得里的資訊
                var features = this.map.queryRenderedFeatures(e.point);
                if(features.length > 0) return;   //有點到其他東西
                this.logicTopo.curKind = "座標";
                let url = "logicTopo/findNodeByKind?kind=地點";
                url += "&lat="+e.lngLat.lat;
                url += "&lng="+e.lngLat.lng;
                this.questArr = [{
                    "curKind": "座標",
                    "name": "位於哪個里",
                    "class":"BaseQuest",
                    "geomUrl": url,
                    "targetKind": "生活區域",
                }];
                this.SelectQuest(0);
            }.bind(this));

            this.map.on("mousemove", function(e){
                if(this.eventFn.onMouseMove) return this.eventFn.onMouseMove(e);
            }.bind(this));

        },
        LoadQuest: function(){
            let transfer = this.logicTopo.transfer[this.logicTopo.curKind];
            if(!transfer) return;
            //console.log(transfer);
            this.questArr = [];
            for(let i=0;i<transfer.length;i++){
                let t = transfer[i];
                //status 0:完成 1:展示 2:沒資料 3:待整理 4:發想中
                let geomUrl = "logicTopo/findNodeByTransfer";
                geomUrl += "?kind="+t["from_類別"];
                geomUrl += "&transfer="+t["類別情境與問題"];
                geomUrl += "&nodeID="+this.logicTopo.nodeID;
                this.questArr.push({
                    "curKind":t["from_類別"],
                    "name": t["類別情境與問題"],
                    "class":t["quest_class"]?t["quest_class"]:"BaseQuest",
                    "geomUrl": geomUrl,
                    "targetKind": t["to_類別"],
                    "status":t["問題狀態"]
                });
            }
        },
        ZoomToBBox: function(quest){
            if(quest.bbox && quest.zoomToBBox){
                //若bbox範圍太小就用zoom數值控制範圍
                let thresh = 0.001;
                if(Math.abs(quest.bbox[0]-quest.bbox[2]) < thresh && Math.abs(quest.bbox[1]-quest.bbox[3]) < thresh){
                    this.map.flyTo({
                        center: [
                            (quest.bbox[0]+quest.bbox[2])*0.5,
                            (quest.bbox[1]+quest.bbox[3])*0.5
                        ],
                        zoom: 15
                    });
                }
                else{
                    this.map.fitBounds([
                        [quest.bbox[0],quest.bbox[1]],
                        [quest.bbox[2],quest.bbox[3]]
                    ]);
                }
            }
        },
        ShowAllBasin: function(){
            if(!this.layer.basin) return;
            this.questArr = [];
            this.layer.basin.show = true;
            this.UpdateLayer();
            this.ZoomToBBox(this.layer.basin);
            toastr.info("請點選要探索的流域");
        },
        SelectBasin: function(basinID){
            this.ClearQuestHistory();
            this.curBasin = basinID;
            this.logicTopo.curKind = "流域";
            this.logicTopo.nodeID = basinID;
            this.LoadQuest();
            this.SelectQuest(0);
            this.layer.basin.show = false;
            this.UpdateLayer();
        },
        UpdateLayer: function(){
            for(let key in this.layer){
                this.layer[key].Update();
            }
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
        OpenQuestInputPanel: function(){
            this.openQuestInputPanel = true;
        },
        CloseQuestInputPanel: function(){
            this.openQuestInputPanel = false;
        },
        ClearQuest: function(item){
            if(item.quest){
                item.quest.ClearAll();
                item.quest = null;
            }
            item.index = -1;
        },
        SelectQuest: function(i){
            this.curQuest.index = i;
            let quest = this.questArr[i];
            let param = {
                "map": this.map,
                "quest": quest
            };
            if(this.curQuest.quest){
                this.curQuest.quest.Stop();
            }
            this.curQuest.quest = new g_QuestClass[quest.class](param);
            this.curQuest.quest.Init((result) => {
                this.UpdateQuestHistory();
                if(this.logicTopo.curKind != quest.targetKind){
                    this.curQuest.index = -1;
                    if(quest.targetKind != null) this.logicTopo.curKind = quest.targetKind;
                }
                this.logicTopo.nodeID = this.curQuest.quest.nodeID;
                this.logicTopo.nodeName = this.curQuest.quest.nodeName;
                this.ZoomToBBox(this.curQuest.quest);
                this.LoadQuest();
            });
            
        },
        UpdateQuestHistory: function(){
            let quest = $.extend({}, this.curQuest);
            this.history.questArr.push(quest);
            if(this.history.questArr.length > this.history.maxSize){
                let diff = this.history.questArr.length-this.history.maxSize;
                for(let i=0;i<diff;i++){
                    this.ClearQuest(this.history.questArr[0]);
                    this.history.questArr.shift();
                }
            }
            this.history.index = this.history.questArr.length-1;
        },
        ClearQuestHistory: function(){
            for(let i=0;i<this.history.questArr.length;i++){
                this.ClearQuest(this.history.questArr[i]); 
            }
            this.history.questArr = [];
            this.history.index = -1;
        },
        SelectQuestHistory: function(i){
            this.history.index = i;
            let item = this.history.questArr[i];
            if(this.curQuest.quest){
                this.curQuest.quest.Stop();
            }
            this.curQuest.index = -1;
            this.curQuest.quest = item.quest;
            this.curQuest.quest.Init(() => {
                this.logicTopo.nodeID = this.curQuest.quest.nodeID;
                this.ZoomToBBox(this.curQuest.quest);
                this.logicTopo.curKind = item.quest.quest.targetKind==null?item.quest.quest.curKind:item.quest.quest.targetKind;
                this.LoadQuest();
            });
        },
        GetNodeInfo: function(kind,nodeID){
            let url = "logicTopo/getNodeInfo?";
            url += "kind="+kind;
            url += "&nodeID="+nodeID;
            $.get(url,(result) => {
                if(result.error){
                    return toastr.error(result.error);
                }
                
            });
        }
    }
});