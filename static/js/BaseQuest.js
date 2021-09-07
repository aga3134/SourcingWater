
class BaseQuest extends BaseLayer{
    constructor(param){
        param.show = true;
        super(param);
        this.quest = param.quest;
        if(!param.onClick){
            this.onClick = (e) => {
                let f = e.features[0];
                if(!f) return;
                g_APP.GetNodeInfo(this.quest.targetKind,f.title);
            };
        }
        this.nodeID = null;
        this.nodeName = "";
        this.setting = {};
    }

    Init(callback){
        let result = []
        let p = new Promise((resolve,reject) => {
            this.LoadData(this.quest.geomUrl,resolve);
        }).then((result) => {
            this.nodeID = result.nodeID;        //用來取資料庫資料
            this.nodeName = result.nodeName;    //用來顯示
            this.setting = result.setting;      //不同display_class會有不同的setting
            if(result.chartArr) this.ShowChart(result.chartArr);
            if(callback) callback(result);
        });
    }

    ClearChart(){
        
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
            }
            g_APP.OpenChartPanel();
        });
    }

    Start(){

    }

    Stop(){
        
    }
}

//讓g_APP可以從config字串new出需要的class，後續繼承的子類別也需要把它們的名字註冊到此變數
g_QuestClass = {"BaseQuest": BaseQuest};