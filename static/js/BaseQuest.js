
class BaseQuest extends BaseLayer{
    constructor(param){
        super(param);
        this.quest = param.quest;
        this.nodeID = null;
        this.nodeName = "";
        this.setting = {};
    }

    Init(callback){
        let promiseArr = [];
        promiseArr.push(new Promise((resolve,reject) => {
            this.LoadData(this.quest.geomUrl,resolve);
        }));
        promiseArr.push(new Promise((resolve,reject) => {
            this.LoadChart(this.quest.chartUrl,resolve);
        }));
        Promise.all(promiseArr).then((values) => {
            let dataResult = values[0];
            this.nodeID = dataResult.nodeID;        //用來取資料庫資料
            this.nodeName = dataResult.nodeName;    //用來顯示
            this.setting = dataResult.setting;      //不同display_class會有不同的setting
            if(callback) callback(values);
        });
    }

    ClearAll(){
        super.ClearAll();
        //clear chart

    }

    LoadChart(url,callback){
        let result = [];
        if(callback) callback(result);
    }
}

//讓g_APP可以從config字串new出需要的class，後續繼承的子類別也需要把它們的名字註冊到此變數
g_QuestClass = {"BaseQuest": BaseQuest};