
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
            if(value.chart) this.ShowChart(value.chart);
            if(callback) callback(result);
        });
    }

    ClearChart(){
        
    }

    ShowChart(chart){
        this.ClearChart();
        var options = {
            chart: {
                type: 'line'
            },
            series: [{
                name: 'sales',
                data: [30,40,35,50,49,60,70,91,125]
            }],
            xaxis: {
                categories: [1991,1992,1993,1994,1995,1996,1997, 1998,1999]
            }
        }
        var chart = new ApexCharts(document.querySelector("#chart"), options);
        chart.render();
        g_APP.OpenChartPanel();
    }

    Start(){

    }

    Stop(){
        
    }
}

//讓g_APP可以從config字串new出需要的class，後續繼承的子類別也需要把它們的名字註冊到此變數
g_QuestClass = {"BaseQuest": BaseQuest};