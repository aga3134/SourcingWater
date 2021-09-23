
class TracePathQuest extends BaseQuest{
    constructor(param){
        super(param);
        this.originPath = [];
        this.displayPath = [];
        this.displayIndex = 0;
        this.timer = null;
        this.zoomToBBox = false;
        this.targetQuest = null;
        this.minIndex = 0;
        this.maxIndex = 0;
    }

    Init(succFn,failFn){
        super.Init((result) => {
            if(!this.targetQuest) this.targetQuest = g_APP.history.questArr[g_APP.history.index].quest;
            this.Play();
            if(succFn) succFn(result);
        }, (reason) => {
            if(failFn) failFn(reason);
        });
        g_APP.OpenPlayerPanel();
        g_APP.player.playFn = (event) => {
            this.Resume();
        };
        g_APP.player.pauseFn = (event) => {
            this.Pause();
        };
        g_APP.player.stopFn = (event) => {
            this.Stop();
        };
    }

    ClearAll(){
        this.Stop();
        super.ClearAll();
    }

    ClearPath(){
        if(this.timer){
            window.clearInterval(this.timer);
            this.timer = null;
        }
        this.displayIndex = 0;
        if(!this.setting) return;
        if(this.displayPath.coordinates){
            this.displayPath.coordinates = [];
            let key = this.GetGeomKey(0);
            this.map.getSource(key).setData(this.displayPath);
        }
    }

    Play(){
        if(!this.setting) return;
        this.ClearPath();
        let targetKey = this.targetQuest.GetGeomKey(0);
        let source = this.targetQuest.sourceHash[targetKey];
        if(!source){
            return toastr.error("鳥覽流路已被刪除");
        }

        let coord = null;
        
        this.minIndex = 0;
        this.maxIndex = 0;
        switch(source.data.type){
            case "FeatureCollection":
                this.maxIndex = source.data.features.length-1;
                if(this.setting.pathIndex < this.minIndex) return toastr.error("河川序號超出範圍");
                if(this.setting.pathIndex > this.maxIndex) return toastr.error("河川序號超出範圍");
                let feature = source.data.features[this.setting.pathIndex];
                this.originPath = feature.geometry;
                if(this.originPath.type != "LineString") return toastr.error("流路格式不符");
                coord = this.originPath.coordinates[0];
                break;
            case "Feature":
                this.originPath = source.data.geometry;
                if(this.originPath.type != "MultiLineString") return toastr.error("流路格式不符");
                coord = this.originPath.coordinates[0][0];
                break;
        }
        this.displayPath = {"type":"LineString","coordinates":[]};
        this.displayPath.coordinates = [coord];

        let key = this.GetGeomKey(0);
        source = this.map.getSource(key);
        if(source) source.setData(this.displayPath);
        
        this.map.flyTo({"center": coord, "zoom": 14, "pitch":35});
        this.map.once("moveend", function(){
            this.Resume();
        }.bind(this));
    }

    Pause(){
        g_APP.player.isPlay = false;
        if(this.timer){
            window.clearInterval(this.timer);
            this.timer = null;
        }
    }

    Resume(){
        if(this.timer) return;
        if(!this.setting) return;
        g_APP.player.isPlay = true;
        let key = this.GetGeomKey(0);

        let coordArr = null;
        switch(this.originPath.type){
            case "LineString":
                coordArr = this.originPath.coordinates;
                break;
            case "MultiLineString":
                coordArr = this.originPath.coordinates[0];
                break;
        }
        
        this.timer = window.setInterval(function(){
            if(this.displayIndex < coordArr.length){
                let coord = coordArr[this.displayIndex];
                this.displayPath.coordinates.push(coord);
                let source = this.map.getSource(key);
                if(source) source.setData(this.displayPath);
                this.map.panTo(coord);
                this.displayIndex++;
            }
            else this.Pause();
        }.bind(this), 100);
    }

    Stop(){
        g_APP.player.isPlay = false;
        this.ClearPath();
        this.map.easeTo({pitch: 30});
        g_APP.ClosePlayerPanel();
    }

}

//需把它們的名字註冊到此變數，讓g_APP可以從config字串new出此類別
g_QuestClass["TracePathQuest"] = TracePathQuest;