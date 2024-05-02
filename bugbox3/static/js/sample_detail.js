import $ from 'jquery';
import DataTable from 'datatables.net-bs5';

$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);
    $('#specimens-table').DataTable({
        order: [[1, 'desc']],
        ordering: false,
        processing: false,
        serverSide: true,
        ajax: {
            url: json_context.specimen_datatables_url,
            dataSrc: 'data'
        },
        language: {
            searchPlaceholder: "Search"
        },
        columns: [
            {
                data: 'data_row',
            }
        ]
    });
})