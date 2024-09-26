import $ from 'jquery';
import DataTable from 'datatables.net-bs5';
import { Tooltip} from 'bootstrap'

$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new Tooltip(tooltipTriggerEl))


    let dt = new DataTable('#images-table', {
        order: [[1, 'desc']],
        ordering: false,
        processing: false,
        serverSide: true,
        ajax: {
            url: json_context.datatables_url,
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
