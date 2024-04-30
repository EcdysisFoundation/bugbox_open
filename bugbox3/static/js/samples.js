import $ from 'jquery';
import DataTable from 'datatables.net-bs5';


$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent)

    $('#samples-table').DataTable({
        order: [[1, 'desc']],
        ordering: false,
        processing: false,
        serverSide: true,
        ajax: {
            url: json_context.samples_datatables_url,
            dataSrc: 'data'
        },
        language: {
            searchPlaceholder: "Search"
        },
        columns: [
            {
                data: 'sample_type',
            },{
                data: 'visit_date',
            },{
                data: 'site_name',
            },
        ]
    });

})