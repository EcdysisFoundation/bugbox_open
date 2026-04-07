import $ from 'jquery';
import DataTable from 'datatables.net-bs5';

function getUrl(dt_url, first_filter, first_check, tags_filter, hide_reviewed) {
    const params = [];
    if (first_filter) {
        params.push('first_filter=' + encodeURIComponent(first_filter));
    }
    if (first_check.prop('checked')) {
        params.push('first_check=' + first_check.prop('checked'));
    }
    if (tags_filter) {
        params.push('tags_filter=' + encodeURIComponent(tags_filter));
    }
    if (hide_reviewed && hide_reviewed.prop('checked')) {
        params.push('hide_reviewed=1');
    }
    const q = params.length ? '?' + params.join('&') : '';
    return `${dt_url}${q}`;
}


$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);

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

        let $hideReviewed = null;
        if (json_context.show_taxonomy_review_filter) {
            $hideReviewed = $(`<input class="form-check-input" type="checkbox" value="" id="hideReviewed">`)
            $('.taxonomy-review-filter').append(
                $('<div class="form-check"></div>').append($hideReviewed).append(
                    $('<label class="form-check-label" for="hideReviewed"></label>').text('Hide reviewed (marked or taxonomy identified)')
                )
            );
        }

        function reloadTableUrl() {
            new_datatables_url = getUrl(
                json_context.datatables_url,
                $firstPicker.val(),
                $firstCheck,
                $tagsPicker.val(),
                $hideReviewed
            );
            data_table.ajax.url(new_datatables_url).load();
        }

        $firstPicker.on('change', reloadTableUrl)
        $tagsPicker.on('change', reloadTableUrl)
        $firstCheck.on('change', reloadTableUrl)
        if ($hideReviewed) {
            $hideReviewed.on('change', reloadTableUrl)
        }

})
