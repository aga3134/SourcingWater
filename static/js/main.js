var g_APP = new Vue({
    el: "#app",
    data: {},
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
            var map = new mapboxgl.Map({
                container: 'map',
                style: 'mapbox://styles/mapbox/satellite-v9',
                center: [121, 24.82],
                pitch: 45,
                zoom: 14
            });
        }
    }
});