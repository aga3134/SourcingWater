class BaseChart{
    constructor(param){
        this.id = param.id;
        this.option = param.option;
        this.chart = null;
    }
    Init(){
        //console.log(this.option);
        this.chart = new ApexCharts(document.querySelector("#"+this.id), this.option);
        this.chart.render();
    }
    Destroy(){
        if(this.chart) this.chart.destroy();
    }
}