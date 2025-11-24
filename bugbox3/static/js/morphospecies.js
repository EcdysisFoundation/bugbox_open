import $ from 'jquery';
import DataTable from 'datatables.net-bs5';

function getUrl(dt_url, first_filter, first_check, tags_filter) {
    let ff = ''
    let fc = ''
    let tf = ''
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
    if (tags_filter) {
        let sep = '?'
        if (ff || fc) {
            sep = '&'
        }
        tf = `${sep}tags_filter=` + tags_filter
    }
    return `${dt_url}${ff}${fc}${tf}`
}


$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent)

    var data_table = $('#data-table').DataTable({
        order: [[1, 'desc']],
        pageLength: 100,
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

      // api_url filters
      let new_datatables_url = '';

      let $firstPicker = $('<select placeholder="Filter by" aria-label="Filter by" id="first-picker" class="form-select"></select>')
        $('.first-picker').append($firstPicker)
        $firstPicker.append(`<option value="">` + json_context.first_picker_text + `</option>`)
        $firstPicker.append(json_context.first_picker_choices.map(value => `<option value="${value[0]}">${value[1]}</option>`))
        $firstPicker.val('')

        let $tagsPicker = $('<select placeholder="Filter by tags" aria-label="Filter by tags" id="tags-picker" class="form-select"></select>')
        $('.tags-picker').append($tagsPicker)
        if (json_context.tags_picker_choices && json_context.tags_picker_choices.length > 0) {
            $tagsPicker.append(`<option value="">` + json_context.tags_picker_text + `</option>`)
            $tagsPicker.append(json_context.tags_picker_choices.map(value => `<option value="${value[0]}">${value[1]}</option>`))
        }
        $tagsPicker.val('')

        let $firstCheck = $(`<input class="form-check-input" type="checkbox" value="" id="firstCheck">`)
        $('.first-check').append($firstCheck)


        $firstPicker.on('change', () => {
            new_datatables_url = getUrl(json_context.datatables_url, $firstPicker.val(), $firstCheck, $tagsPicker.val())
            data_table.ajax.url( new_datatables_url ).load();
        })
        $tagsPicker.on('change', () => {
            new_datatables_url = getUrl(json_context.datatables_url, $firstPicker.val(), $firstCheck, $tagsPicker.val())
            data_table.ajax.url( new_datatables_url ).load();
        })
        $firstCheck.on('change', () => {
            new_datatables_url = getUrl(json_context.datatables_url, $firstPicker.val(), $firstCheck, $tagsPicker.val())
            data_table.ajax.url( new_datatables_url ).load();
        })

})
