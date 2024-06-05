import $ from 'jquery';
import DataTable from 'datatables.net-bs5';

// Basic datatable with optional filtering
// Requries json_context.datatables_url
// Requires json_context.first_picker_choices
// first_picker_choices can be None
// Requires json_context.first_picker_text if json_context.first_picker_choices



$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent)

    var data_table = $('#data-table').DataTable({
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
})
