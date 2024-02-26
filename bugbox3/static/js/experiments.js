import $ from 'jquery';
import DataTable from 'datatables.net-bs5';


$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent)

    $('#experiments-table').DataTable({
        order: [[1, 'desc']],
        ordering: false,
        processing: false,
        serverSide: true,
        ajax: {
            url: json_context.experiments_datatables_url,
            dataSrc: 'data'
        },
        language: {
            searchPlaceholder: "Search"
        },
        columns: [
            {
                data: 'experiment_link',
            },{
                data: 'abbreviation',
            },{
                data: 'year_span',
            },{
                data: 'total_samples',
            },{
                data: 'photo_sampling',
            },{
                data: 'not_reviewed'
            },
        ]
    });

})