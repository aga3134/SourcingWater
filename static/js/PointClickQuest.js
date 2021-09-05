
class PointClickQuest extends BaseQuest{
    constructor(param){
        super(param);
    }
}

//需把它們的名字註冊到此變數，讓g_APP可以從config字串new出此類別
g_QuestClass["PointClickQuest"] = PointClickQuest;