
class TracePathQuest extends BaseQuest{
    constructor(param){
        super(param);
        this.originPath = [];
        this.displayPath = [];
        this.displayIndex = 0;
        this.timer = null;
    }

    Init(callback){
        super.Init(() => {
            this.Play();
            if(callback) callback();
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
            this.displayPath.coordinates[0] = [];
            let key = this.GetGeomKey(this.setting.pathIndex);
            this.map.getSource(key).setData(this.displayPath);
        }
    }

    Play(){
        if(!this.setting) return;
        this.ClearPath();
        let key = this.GetGeomKey(this.setting.pathIndex);
        let source = this.sourceHash[key];
        this.originPath = source.data.geometry;
        this.displayPath = $.extend(true, {}, source.data.geometry);
        let coord = this.originPath.coordinates[0];
        this.displayPath.coordinates[0] = [coord[0]];

        source = this.map.getSource(key);
        if(source) source.setData(this.displayPath);
        
        this.map.flyTo({"center": coord[0], "zoom": 14, "pitch":35});
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
        let key = this.GetGeomKey(this.setting.pathIndex);
        let coord = this.originPath.coordinates[0];
        this.timer = window.setInterval(function(){
            if(this.displayIndex < coord.length){
                this.displayPath.coordinates[0].push(coord[this.displayIndex]);
                let source = this.map.getSource(key);
                if(source) source.setData(this.displayPath);
                this.map.panTo(coord[this.displayIndex]);
                this.displayIndex++;
            }
            else Pause();
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