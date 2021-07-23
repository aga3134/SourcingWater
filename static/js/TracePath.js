
class TracePath extends BaseQuest{
    constructor(param){
        super(param);
        this.originPath = [];
        this.displayPath = [];
        this.pathIndex = param.quest.setting.pathIndex;
        this.displayIndex = 0;
        this.timer = null;
    }

    Init(){
        this.LoadData(() => {
            this.Play();
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
        if(this.displayPath.coordinates){
            this.displayPath.coordinates[0] = [];
            var key = this.GetGeomKey(this.pathIndex);
            this.map.getSource(key).setData(this.displayPath);
        }
    }

    Play(){
        this.ClearPath();
        var key = this.GetGeomKey(this.pathIndex);
        var source = this.sourceHash[key];
        this.originPath = source.data;
        this.displayPath = $.extend(true, {}, source.data);
        var coord = this.originPath.coordinates[0];
        this.displayPath.coordinates[0] = [coord[0]];

        var source = this.map.getSource(key);
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
        g_APP.player.isPlay = true;
        var key = this.GetGeomKey(this.pathIndex);
        var coord = this.originPath.coordinates[0];
        this.timer = window.setInterval(function(){
            if(this.displayIndex < coord.length){
                this.displayPath.coordinates[0].push(coord[this.displayIndex]);
                var source = this.map.getSource(key);
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
g_QuestClass["TracePath"] = TracePath;