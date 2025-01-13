import $ from 'jquery';
import DataTable from 'datatables.net-bs5';


$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent)

    function getUrl(dt_url, org_filter) {
        let url_str = ''
        let params = []
        params.push('org=' + org_filter)
        for ( let i = 0; i < params.length; i++) {
            let sep = '&'
            if (i == 0) {
                sep = '?'
            }
            url_str += `${sep}${params[i]}`;
        }
        return `${dt_url}${url_str}`
    }

    function reloadUrl() {
        experiments_table.ajax.url( getUrl(
                json_context.experiments_datatables_url,
                $orgPicker.val()
            )).load();
    }
    let url = getUrl(json_context.experiments_datatables_url, String(json_context.org_choices[0][0]))

    var experiments_table = $('#experiments-table').DataTable({
        order: [[1, 'desc']],
        ordering: false,
        processing: false,
        serverSide: true,
        ajax: {
            url: url,
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

    let $orgPicker = $(`<select id="org-filter" class="form-select"></select>`)
    $('.org-picker').append($orgPicker)
    $orgPicker.append(json_context.org_choices.map(value=>`<option value="${value[0]}">${value[1]}</option>`))

    $orgPicker.on('change', () => {
        reloadUrl();
    })

})
