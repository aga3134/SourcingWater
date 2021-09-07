
class DataInputQuest extends BaseQuest{
    constructor(param){
        super(param);
    }
    Init(callback){
        super.Init((result) => {
            Vue.set(g_APP.questInput,"config",this.setting.inputConfig);
            g_APP.questInput.updateFn = () => {
                //console.log(this.quest.geomUrl);
                let urlString = this.quest.geomUrl.split("?");
                var params = new URLSearchParams(urlString[1]);
                for(let key in g_APP.questInput.config){
                    let p = g_APP.questInput.config[key];
                    params.set(p.variable,p.value);
                }
                this.quest.geomUrl = urlString[0]+"?"+params.toString();
                //console.log(this.quest.geomUrl);
                this.Init();
            };
            g_APP.OpenQuestInputPanel();
            if(callback) callback(result);
        });
    }
}

//需把它們的名字註冊到此變數，讓g_APP可以從config字串new出此類別
g_QuestClass["DataInputQuest"] = DataInputQuest;