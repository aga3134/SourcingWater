
class BaseQuest extends BaseLayer{
    constructor(param){
        param.show = true;
        super(param);
        this.updateHistory = true;
        this.quest = param.quest;
        this.selectSource = null;
        this.selectFeature = null;
        if(!param.onClick){
            this.onClick = (e) => {
                let f = e.features[0];
                if(!f) return;
                //update feature state
                if(this.selectSource != null && this.selectFeature != null){
                    this.map.setFeatureState(
                        {source: this.selectSource, id: this.selectFeature},
                        {selected: false}
                    );
                    this.selectSource = null;
                    this.selectFeature = null;
                }
                this.selectSource = f.source;
                this.selectFeature = f.id;
                if(this.selectSource != null && this.selectFeature != null){
                    this.map.setFeatureState(
                        {source: f.source, id: f.id},
                        {selected: true}
                    );
                }
                //console.log(f);
                if(f.properties.popup){
                    let popup = JSON.parse(f.properties.popup);
                    let pt = f.geometry.coordinates;
                    let content = "<div class='popup'>";
                    if(popup.photo){
                        content += "<a href='"+popup.photo+"' target='_blank'>";
                        content += "<img class='photo' src='"+popup.photo+"'>";
                        content += "</a>";
                    }
                    if(popup.title){
                        content += "<div class='title'>"+popup.title+"</div>";
                    }
                    if(popup.desc){
                        content += "<div>"+popup.desc+"</div>";
                    }
                    
                    if(g_APP.infoWindow){
                        g_APP.infoWindow.remove();
                    }
                    g_APP.infoWindow = new mapboxgl.Popup({
                        closeOnClick: false,
                        maxWidth:"100%"
                    })
                    .setLngLat([pt[0], pt[1]])
                    .setHTML(content)
                    .addTo(g_APP.map);
                }
                g_APP.SelectNode(this.quest.targetKind,f.properties.id,f.properties.name);
            };
        }
        this.nodeID = null;
        this.nodeName = "";
        this.setting = {};
        this.chartInstance = {};
    }

    Init(succFn,failFn){
        let result = []
        let p = new Promise((resolve,reject) => {
            this.LoadData(this.quest.geomUrl,resolve,reject);
        }).then((result) => {
            //預設選擇第一個物件
            let key = this.GetGeomKey(0)
            let source = this.map.getSource(key);
            if(source){
                this.selectSource = key;
                this.selectFeature = 0;
                this.map.setFeatureState(
                    {source: this.selectSource, id: this.selectFeature},
                    {selected: true}
                );
            }
            this.nodeID = result.nodeID;        //用來取資料庫資料
            this.nodeName = result.nodeName;    //用來顯示
            this.setting = result.setting;      //不同display_class會有不同的setting
            if(result.chartArr) this.ShowChart(result.chartArr);
            this.inited = true;
            if(succFn) succFn(result);
        }, (reason) => {
            if(failFn) failFn(reason);
        });
    }

    ClearChart(){
       for(let key in this.chartInstance){
        let chart = this.chartInstance[key];
        chart.Destroy();
       }
       this.chartInstance = {};
    }  

    ShowChart(chartArr){
        this.ClearChart();
        g_APP.chartArr = chartArr;
        Vue.nextTick(() => {
            for(let i=0;i<chartArr.length;i++){
                let chartData = chartArr[i];
                let id = "chart"+i;
                let param = {
                    "id": id,
                    "option": chartData.option,
                }
                let chart = new BaseChart(param);
                chart.Init();
                this.chartInstance[id] = chart;
            }
            g_APP.OpenChartPanel();
        });
    }

    ClearAll(){
        this.ClearChart();
        super.ClearAll();
    }

    Start(){

    }

    Stop(){
        this.ClearChart();
    }
}

//讓g_APP可以從config字串new出需要的class，後續繼承的子類別也需要把它們的名字註冊到此變數
g_QuestClass = {"BaseQuest": BaseQuest};