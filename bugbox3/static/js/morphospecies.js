import $ from 'jquery';
import DataTable from 'datatables.net-bs5';

function getUrl(dt_url, first_filter, first_check) {
    let ff = ''
    let fc = ''
    if (first_filter) {
        ff = '?first_filter=' + first_filter;
    }
    if (first_check.prop("checked")) {
        let sep = '?'
        if (ff) {
            sep = '&'
        }
        fc = `${sep}first_check=` + first_check.prop("checked")
    }
    return `${dt_url}${ff}${fc}`
}


$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent)

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
                data: 'data_row',
            }
        ]
    });

      // api_url filters
      let new_datatables_url = '';

      let $firstPicker = $('<select placeholder="Filter by" aria-label="Filter by" id="first-picker" class="form-select"></select>')
        $('.first-picker').append($firstPicker)
        $firstPicker.append(`<option value="">` + json_context.first_picker_text + `</option>`)
        $firstPicker.append(json_context.first_picker_choices.map(value => `<option value="${value[0]}">${value[1]}</option>`))
        $firstPicker.val('')

        let $firstCheck = $(`<input class="form-check-input" type="checkbox" value="" id="firstCheck">`)
        $('.first-check').append($firstCheck)


        $firstPicker.on('change', () => {
            new_datatables_url = getUrl(json_context.datatables_url, $firstPicker.val(), $firstCheck)
            data_table.ajax.url( new_datatables_url ).load();
        })
        $firstCheck.on('change', () => {
            new_datatables_url = getUrl(json_context.datatables_url, $firstPicker.val(), $firstCheck)
            data_table.ajax.url( new_datatables_url ).load();
        })

})
