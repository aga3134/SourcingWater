class BaseChart{
    constructor(param){
        this.id = param.id;
        this.option = param.option;
    }
    Init(){
        let chart = new ApexCharts(document.querySelector("#"+this.id), this.option);
        chart.render();
    }
}