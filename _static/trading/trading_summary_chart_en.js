Highcharts.chart('container', {
    chart: {
        type: 'spline'
    },
    accessibility: {
        enabled: false
    },
    title: {
        text: chart_title
    },
    tooltip: {
        enabled: false
    },
    legend: {
        enabled: false
    },
    xAxis: {
        tickInterval: 1,
        title: {
            text: x_title
        },
        min: 1,
        max: 10
    },
    yAxis: {
        title: {
            text: y_title
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
            data: js_vars.average_prices
        }
    ],
    credits: {
       enabled: false
    }
});