var g_APP = new Vue({
    el: "#app",
    data: {
        map: null,
        openOptionPanel: false,
        openQuestPanel: false,
        openChartPanel: false,
        openAboutPanel: false,
        questArr: [],
        curQuest: {
            quest: null,
            source: {},
            layer: {},
            chart: {},
            option: {},
        },
        tracePath:{
            originPath: [],
            displayPath: [],
            curIndex: 0,
            timer: null
        }
    },
    delimiters: ['[[',']]'],    //vue跟jinja的語法會衝突
    created: function(){
        window.addEventListener('load', function() {
            this.InitMap(function(){
                this.LoadQuest();
            }.bind(this));
        }.bind(this));
    },
    methods:{
        InitMap: function(callback){
            var accessToken = $("meta[name='accessToken']").attr("content");
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
                this.map.flyTo({
                    center: [121, 24.82],
                    pitch: 30,
                    zoom: 14,
                    bearing: 0,
                    speed: 0.5,
                    essential: true
                });
                
                //add search box
                var geocoder = new MapboxGeocoder({
                    accessToken: mapboxgl.accessToken,
                    placeholder: "搜尋地點",
                    mapboxgl: mapboxgl
                });
                document.getElementById('geocoder').appendChild(geocoder.onAdd(this.map));

                if(callback) callback();
            }.bind(this));
        },
        LoadQuest: function(){
            this.questArr = [
                {
                    "quest": "頭前溪長怎麼?",
                    "geom": [
                        {
                            "title": "頭前溪",
                            "type": "line",
                            "url": "topo/river",
                            "paint": {
                                "line-color": "#f33",
                                "line-width": 4
                            }
                        }
                    ],
                    "chart": [],
                    "option": [],
                    "action":{}
                },
                {
                    "quest": "水從頭前溪源頭流到海洋走什麼路徑?",
                    "geom": [
                        {
                            "title": "頭前溪路徑",
                            "type": "line",
                            "url": "topo/river",
                            "paint": {
                                "line-color": "#33f",
                                "line-width": 4
                            }
                        }
                    ],
                    "chart": [],
                    "option": [],
                    "action":{
                        "func": "TracePath",
                        "param":{
                            "index": 0
                        }
                    }
                }
            ];
            this.SelectQuest(0);
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
        ClearQuest: function(){
            for(var key in this.curQuest.layer){
                this.map.removeLayer(this.curQuest.layer[key].name);
            }
            this.curQuest.layer = {};

            for(var key in this.curQuest.source){
                this.map.removeSource(this.curQuest.source[key].name);
            }
            this.curQuest.source = {};

            //clear charts

            //clear option UI
            
            //clear action
            if(this.tracePath.timer){
                window.clearInterval(this.tracePath.timer);
                this.tracePath.timer = null;
            }
        },
        SelectQuest: function(i){
            this.ClearQuest();

            var q = this.questArr[i];
            this.curQuest.quest = q.quest;

            var promiseArr = [];
            for(let i=0;i<q.geom.length;i++){
                let geom = q.geom[i];
                promiseArr.push(new Promise((resolve,reject) => {
                    $.get(geom.url, (data) => {
                        var key = this.ToHash(q.quest)+"_"+i;
                        //console.log(key);
                        this.map.addSource(key, {
                            "type": "geojson",
                            "data": data
                        });
                        this.map.addLayer({
                            "id": key,
                            "type": geom.type,
                            "source": key,
                            "paint": geom.paint
                        });
                        this.curQuest.source[key] = {"name":key, "data":data};
                        this.curQuest.layer[key] = {"name":key};
                        resolve(key);
                    });
                }));
            }

            //add charts

            //add option UI

            //call action
            Promise.all(promiseArr).then((keyArr) => {
                //console.log(keyArr);
                if(q.action.func in this) this[q.action.func](q.action.param);
            });

        },
        TracePath: function(param){
            var key = this.ToHash(this.curQuest.quest)+"_"+param.index;
            
            var ClearTimer = function(){
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
                var source = this.curQuest.source[key];
                this.tracePath.originPath = source.data;
                this.tracePath.displayPath = $.extend(true, {}, source.data);
                var coord = this.tracePath.originPath.coordinates[0];
                this.tracePath.displayPath.coordinates[0] = [coord[0]];
                this.tracePath.curIndex = 0;
                var source = this.map.getSource(key);
                if(source) source.setData(this.tracePath.displayPath);
                
                this.map.flyTo({"center": coord[0], "zoom": 14, "pitch":35});
                this.map.once("moveend", function(){
                    this.tracePath.timer = window.setInterval(function(){
                        if(this.tracePath.curIndex < coord.length){
                            this.tracePath.displayPath.coordinates[0].push(coord[this.tracePath.curIndex]);
                            var source = this.map.getSource(key);
                            if(source) source.setData(this.tracePath.displayPath);
                            this.map.panTo(coord[this.tracePath.curIndex]);
                            this.tracePath.curIndex++;
                        }
                        else ClearTimer();
                    }.bind(this), 100);
                }.bind(this));
            }
        },
        ToHash: function(str){
            var hash = 0, i, chr;
            if (str.length === 0) return hash;
            for (i = 0; i < str.length; i++) {
                chr   = str.charCodeAt(i);
                hash  = ((hash << 5) - hash) + chr;
                hash |= 0; // Convert to 32bit integer
            }
            return hash;
        },
    }
});