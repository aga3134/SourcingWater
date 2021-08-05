
class BaseQuest extends BaseLayer{
    constructor(param){
        param.show = true;
        super(param);
        this.quest = param.quest;
        this.nodeID = null;
        this.nodeName = "";
        this.setting = {};
    }

    Init(callback){
        let result = []
        let p = new Promise((resolve,reject) => {
            this.LoadData(this.quest.geomUrl,resolve);
        }).then((value) => {
            this.nodeID = value.nodeID;        //用來取資料庫資料
            this.nodeName = value.nodeName;    //用來顯示
            this.setting = value.setting;      //不同display_class會有不同的setting
            if(value.chartArr) this.ShowChart(value.chartArr);
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