import $ from 'jquery';
import DataTable from 'datatables.net-bs5';

function getDescription(data, type, row) {
    return `
<ul class="list-group list-group-flush">
  <li class="list-group-item"><b>Order:</b> ${row.taxonomy.gbif_order}</li>
  <li class="list-group-item"><b>Family:</b> ${row.taxonomy.gbif_family}</li>
  <li class="list-group-item"><b>Species:</b> <i>${row.taxonomy.species}</i></li>
  <li class="list-group-item">${row.details.visit_date} | ${row.details.location}</li>
  <li class="list-group-item">${row.details.archival}</li>
</ul>
`
}

$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);

    var data_table = $('#data-table').DataTable({
        order: [[1, 'desc']],
        pageLength: 100,
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
                data: 'image',
            },
            {
                data: '',
                render: getDescription
            }
        ],
        columnDefs: [
            {
                targets: 0,
                className: 'dt-body-right'
            }
        ]
    });

});

