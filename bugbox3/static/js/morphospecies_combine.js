import $ from 'jquery';
import DataTable from 'datatables.net-bs5';


$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent)
    let combine_to_id = document.getElementById('combine_to_id');
    var data_table = $('#data-table').DataTable({
        order: [[1, 'desc']],
        ordering: false,
        processing: true,
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

    $('#data-table').on('click', 'tr', function () {
        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected');
        } else {
            data_table.$('tr.selected').removeClass('selected');
            $(this).addClass('selected');
        }
    });

    // api_url filters
    let new_datatables_url = ''
    if (json_context.first_picker_choices) {
    let $firstPicker = $('<select placeholder="Filter by" aria-label="Filter by" id="first-picker" class="form-select"></select>')
    $('.first-picker').append($firstPicker)
    $firstPicker.append(`<option value="">` + json_context.first_picker_text + `</option>`)
    $firstPicker.append(json_context.first_picker_choices.map(value => `<option value="${value[0]}">${value[1]}</option>`))
    $firstPicker.val('')
    $firstPicker.on('change', () => {
        new_datatables_url = json_context.datatables_url  + '?first_filter=' + $firstPicker.val()
        data_table.ajax.url( new_datatables_url ).load();
    })
    };
    let $selectMorphoButton = $('<input type="submit" class="btn btn-info" data-bs-dismiss="modal" value="Combine with selected"></input>')
    $('.select-morpho-button').append($selectMorphoButton)
    $selectMorphoButton.on('click', function() {
        let data = data_table.rows('.selected').data();
        if (data.length == 1) {
            data = data[0]
            combine_to_id.value = data.id;
        }
    })


})
