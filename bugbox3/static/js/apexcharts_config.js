import $ from 'jquery';
import ApexCharts from 'apexcharts';

// requires a json_context

$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);

    if ('ai_accuracy_over_time' in json_context) {
        // requires <div id="ai_accuracy_over_time"></div> in template
        var options = {
            series: [
              {
                name: 'precision',
                data: json_context.ai_accuracy_over_time.precision
              },
              {
                name: 'recall',
                data: json_context.ai_accuracy_over_time.recall
              },
              {
                name: 'f1',
                data: json_context.ai_accuracy_over_time.f1
              },
            ],
            chart: {
              type: 'line',
            },


            xaxis: {
              type: 'datetime',
            },
            yaxis: {
              min: 0,
              max: 1.0,
              decimalsInFloat: 1,
            }
          };


          var chart = new ApexCharts(document.querySelector("#ai_accuracy_over_time"), options);
          if ( json_context.ai_accuracy_over_time.train.length ) {
            chart.render();
          }
    }

});
