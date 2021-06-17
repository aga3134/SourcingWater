var g_APP = new Vue({
    el: "#app",
    data: {
        map: null,
        openOptionPanel: false,
        openQuestPanel: false,
        openChartPanel: false,
        openAboutPanel: false
    },
    delimiters: ['[[',']]'],    //vue跟jinja的語法會衝突
    created: function(){
        window.addEventListener('load', function() {
            this.InitMap();
        }.bind(this));
        
    },
    methods:{
        InitMap: function(){
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
                    pitch: 45,
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

                //load geojson data
                $.get("topo/river", function(data){
                    //console.log(data);
                    this.map.addSource('route', {
                        'type': 'geojson',
                        'data': data
                    });
                    this.map.addLayer({
                        'id': 'route',
                        'type': 'line',
                        'source': 'route',
                        'layout': {
                            'line-join': 'round',
                            'line-cap': 'round'
                        },
                        'paint': {
                            'line-color': '#f33',
                            'line-width': 4
                        }
                    });
                }.bind(this));
            }.bind(this));
        },
        SetMapPadding: function(padding){
            var p = this.map.getPadding();
            if("left" in padding) p.left = padding.left;
            if("right" in padding) p.right = padding.right;
            if("top" in padding) p.top = padding.top;
            if("bottom" in padding) p.bottom = padding.bottom; 
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
    }
});