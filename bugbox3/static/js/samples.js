import $ from 'jquery';
import DataTable from 'datatables.net-bs5';

function getDetail( row ) {
    return row.sample_type
}


$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent)

    var samples_table = $('#samples-table').DataTable({
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
        preDrawCallback: function (settings) {
            var api = new $.fn.dataTable.Api(settings);
            var pagination = $(this)
                .closest('.dataTables_wrapper')
                .find('.dataTables_paginate');
            pagination.toggle(api.page.info().pages > 1);
        },
        columns: [
            {
                class: 'details-control',
                orderable: false,
                data: null,
                defaultContent: '',
            },{
                data: 'sample_type',
            },{
                data: 'visit_date',
            },{
                data: 'site_name',
            },
        ]
    });

    // Array to track the ids of the details displayed rows in beekeeper_table
    var detailRows = [];
    $('#samples-table tbody').on( 'click', 'tr td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = samples_table.row(tr);
        var idx = detailRows.indexOf(tr.attr('id'));
 
        if (row.child.isShown()) {
            tr.removeClass('details');
            row.child.hide();
 
            // Remove from the 'open' array
            detailRows.splice(idx, 1);
        } else {
            tr.addClass('details');
            row.child(getDetail(row.data())).show();
 
            // Add to the 'open' array
            if (idx === -1) {
                detailRows.push(tr.attr('id'));
            }
        }
    });
    // On each draw, loop over the `detailRows` array and show any child rows
    samples_table.on('draw', function () {
        detailRows.forEach(function(id, i) {
            $('#' + id + ' td.details-control').trigger('click');
        });
    });

})