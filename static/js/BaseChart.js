class BaseChart{
    constructor(param){
        this.id = param.id;
        this.option = param.option;
    }
    Init(){
        //console.log(this.option);
        let chart = new ApexCharts(document.querySelector("#"+this.id), this.option);
        chart.render();
    }
}