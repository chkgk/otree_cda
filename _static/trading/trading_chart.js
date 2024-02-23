let price_chart = Highcharts.chart('container', {
    chart: {
        type: 'spline'
    },
    accessibility: {
        enabled: false
    },
    title: {
        text: ''
    },
    tooltip: {
        enabled: false
    },
    legend: {
        enabled: false
    },
    xAxis: {
        tickInterval: 20,
        title: {
            text: 'Seconds'
        },
        min: 0,
        max: 120
    },
    yAxis: {
        title: {
            text: 'Points'
        },
        min: 0,
    },
    
    plotOptions: {
        series: {
            marker: {
                symbol: 'circle',
                fillColor: '#FFFFFF',
                enabled: true,
                radius: 2.5,
                lineWidth: 1,
                lineColor: null
            },
            label: {
                enabled: false
            }
        }
    },

    colors: ['#06C', '#036', '#000'],
    
    series: [
        {
            data: [
                
            ]
        }
    ],
    credits: {
       enabled: false
    }
});