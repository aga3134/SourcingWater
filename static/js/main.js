let g_APP = new Vue({
    el: "#app",
    data: {
        map: null,
        wmtsBarrier: null,
        isLoading: true,
        isProcessing: false,
        openOptionPanel: false,
        openQuestPanel: false,
        openChartPanel: false,
        openAboutPanel: false,
        openPlayerPanel: false,
        openQuestInputPanel: false,
        openInfoPanel: false,
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
            swcbMap: null,
            uavMap: null,
            //irrigationMap: null,
            commutag: null
        },
        commutag:{
            dataset:"60c0307db652fe1483444844"
        },
        eventFn:{
            onMouseMove: null,
            onClick:null
        },
        nodeInfo:{},
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
                {name:"marker-black",url:"static/image/marker-black-24.png"},
                {name:"marker-orange",url:"static/image/marker-orange-24.png"},
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
                        url: "layer/commutag?dataset="+this.commutag.dataset,
                        onClick: (e) => {
                            let f = e.features[0];
                            if(!f) return;
                            let pt = f.geometry.coordinates;
                            let content = "<div class='commutag'>";
                            content += "<a href='"+f.properties.url+"' target='_blank'>";
                            content += "<img class='photo' src='"+f.properties.photo+"'>";
                            content += "</a>";
                            if(f.properties["名稱"]){
                                content += "<div class='title'>"+f.properties["思源地圖名稱"]+"</div>";
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

                            if(f.properties["思源地圖類別"] && f.properties["思源地圖名稱"]){
                                this.logicTopo.curKind = f.properties["思源地圖類別"];
                                this.logicTopo.nodeID = this.curQuest.nodeID = f.properties["思源地圖名稱"];
                                this.logicTopo.nodeName = this.curQuest.nodeName = f.properties["思源地圖名稱"];
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
                //style: 'mapbox://styles/aga3134/cktf22irw2v2d19pjwuxxjb9v',
                center: [121, 23.7],
                zoom: 6.5,
                fadeDuration: 0,    //避免鳥覽symbol更新時因為fade in看不到
            });
            
            this.map.on('load', function(){
                //取得衛星圖之後的第一個layer，之後的wmts layer都會加在它前面，避免蓋掉後面的地理資訊
                const layers = this.map.getStyle().layers;
                let lastLayer = null;
                for(const layer of layers) {
                    if(lastLayer == "satellite"){
                        this.wmtsBarrier = layer.id;
                        break;
                    }
                    lastLayer = layer.id;
                }

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
                this.layer.LUIMap = new WMTSLayer({
                    map:this.map,
                    show:false,
                    urlTemplate:"https://wmts.nlsc.gov.tw/wmts/{mapName}/default/GoogleMapsCompatible/{z}/{y}/{x}",
                    urlVariable:{
                        mapName: "LUIMAP01"
                    }
                });

                //水保地圖
                this.layer.swcbMap = new WMTSLayer({
                    map:this.map,
                    show:false,
                    urlTemplate:"https://storage.geodac.tw/Tile/v2/{mapName}/{z}/{y}/{x}.jpg ",
                    urlVariable:{
                        mapName: "SWCBProject/Taiwan_Rmap_20m"
                    }
                });

                //圳路圖層(太糊不使用)
                /*this.layer.irrigationMap = new WMTSLayer({
                    map: this.map,
                    show: false,
                    url: "https://irrggis.aerc.org.tw/arcgis/services/WMS/OpenData/MapServer/WmsServer?bbox={bbox-epsg-3857}&format=image/png&service=WMS&version=1.1.1&request=GetMap&srs=EPSG:3857&transparent=true&width=512&height=512&layers=0&styles=default"
                })*/


                if(callback) callback();
            }.bind(this));

            this.map.on('click', function(e) {
                if(this.eventFn.onClick) return this.eventFn.onClick(e);
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
                geomUrl += "&nodeName="+this.logicTopo.nodeName;
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
            //this.ClearQuestHistory();
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
                if(!this.layer[key]) continue;
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
        OpenInfoPanel: function(){
            this.openInfoPanel = true;
        },
        CloseInfoPanel: function(){
            this.openInfoPanel = false;
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
            if(!this.curQuest.quest.updateHistory) return;
            
            let quest = $.extend({}, this.curQuest);
            //刪除所選歷史探索之後的所有歷史探索再加上新的探索
            if(this.history.index < this.history.questArr.length-1){
                for(let i=this.history.questArr.length-1;i>this.history.index;i--){
                    this.ClearQuest(this.history.questArr[i]); 
                    this.history.questArr.splice(i,1);
                }
            }
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
            this.curQuest.quest.show = true;
            this.curQuest.quest.Init(() => {
                this.logicTopo.nodeID = this.curQuest.quest.nodeID;
                this.logicTopo.nodeName = this.curQuest.quest.nodeName;
                this.ZoomToBBox(this.curQuest.quest);
                this.logicTopo.curKind = item.quest.quest.targetKind==null?item.quest.quest.curKind:item.quest.quest.targetKind;
                this.LoadQuest();
            });
        },
        RemoveQuestHistory: function(i){
            let q = this.history.questArr[i];
            //if(confirm("確定刪除回溯探索「"+q.quest.quest.name+" - "+q.quest.nodeName+"」?")){
                this.ClearQuest(this.history.questArr[i]); 
                this.history.questArr.splice(i,1);
            //}
        },
        RemoveAllQuestHistory: function(){
            if(confirm("確定刪除所有回溯探索?")){
                for(let i=0;i<this.history.questArr.length;i++){
                    let q = this.history.questArr[i];
                    this.ClearQuest(this.history.questArr[i]); 
                }
                this.history.questArr = [];
            }
        },
        SelectNode: function(kind,nodeID,nodeName){
            this.logicTopo.nodeID = this.curQuest.quest.nodeID = nodeID;
            this.logicTopo.nodeName = this.curQuest.quest.nodeName = nodeName;
            this.logicTopo.curKind = kind;
            this.LoadQuest();
        },
        GetNodeInfo: function(){
            let url = "logicTopo/getNodeInfo?";
            url += "kind="+this.logicTopo.curKind;
            url += "&nodeID="+this.logicTopo.nodeID;
            url += "&nodeName="+this.logicTopo.nodeName;
            $.get(url,(result) => {
                if(result.error){
                    return toastr.error(result.error);
                }
                if(result.urls){
                    result.urls = result.urls.split("|");
                }
                this.nodeInfo = result;
                //console.log(this.nodeInfo);
                this.OpenInfoPanel();
            });
        },
        ReloadCommutag: function(){
            if(!this.layer.commutag) return;
            this.layer.commutag.url = "layer/commutag?dataset="+this.commutag.dataset;
            this.layer.commutag.Init();
        }
    }
});