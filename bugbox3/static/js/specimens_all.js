import $ from 'jquery';
import DataTable from 'datatables.net-bs5';


$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);
    let json_data = {
        confirm_ids: [],  // specimen ids
        reject_ids: [],  // specimen ids
        new_classifications: {},  // key:value pairs of specimen_id: morphospecies_id
    };
    function resetJsonData() {
        json_data = {
            confirm_ids: [],  // specimen ids
            reject_ids: [],  // specimen ids
            new_classifications: {},  // key:value pairs of specimen_id: morphospecies_id
        };
    }


let usStateChoices = json_context.state_choices_dict.US_STATE_CHOICES
let caStateChoices = json_context.state_choices_dict.CANADA_STATE_CHOICES

function getUrl(dt_url,
        acceptance_filter, archival_check, user_filter,
        country_filter, state_filter, tag_filter, sample_type_filter
    ) {
    let url_str = ''
    let params = []
    if (acceptance_filter) {
        params.push('acceptance=' + acceptance_filter);
    }
    if (archival_check.prop("checked")) {
        params.push('archival=' + archival_check.prop("checked"));
    }
    if (user_filter) {
        params.push('user=' + user_filter);
    }
    if (country_filter) {
        params.push('country=' + country_filter);
    }
    if (state_filter) {
        params.push('state=' + state_filter);
    }
    if (tag_filter) {
        params.push('tag=' + tag_filter);
    }
    if (sample_type_filter) {
        params.push('sample_type=' +sample_type_filter);
    }
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
    specimens_table.ajax.url( getUrl(
            json_context.datatables_url,
            $acceptancePicker.val(), $archivalCheck, $userPicker.val(),
            $countryPicker.val(), $statePicker.val(), $tagPicker.val(),
            $sampleTypePicker.val()
        )).load();
    resetJsonData()
}


function doMyThing(recipient) {
    if (recipient) {
        let thisRecipient = document.getElementById(recipient);
        let data = data_table_2.rows('.selected').data();
        if (data.length == 1) {
            data = data[0];
            thisRecipient.value = data.name;
            let id = recipient.replace('new-class-', '');
            json_data.new_classifications[id] = data.id;
            let rejectCheck = 'reject-' + id;
            document.getElementById(rejectCheck).checked = true;

        }
    }
}

function clearSelection(recipient) {
    if (recipient) {
        let thisRecipient = document.getElementById(recipient);
        thisRecipient.value = '';
        let id = recipient.replace('new-class-', '')
        delete json_data.new_classifications[id]
    }
}

function formatRowDiv (cols) {
    return `<div class='row'>${cols}</div>`;
}

function formatColDiv (col) {
    return `<div class=\"col\">${col}</div>`;
}

function get_archival (row) {
    if (row.archival_identifier) {
        return `${row.archival_identifier}<br/>${row.archival_preservation}<br/>${row.archival_stored}`
    } else {
        return ''
    }
}


function getRow ( data, type, row ) {
    let cols = ''
    let view_edit = `<h5><a href="${row.view_link}" target="_blank"><i class="bi bi-eye"></i></a>
<a href="${row.edit_link}" target="_blank"><i class="bi bi-pencil"></i></a></h5>`
    // img_thumbnail
    if (row.img_thumbnail_large) {
        cols += formatColDiv(`<button type="button" class="btn" data-bs-toggle="modal"
                data-bs-target="#imageModal"
                data-bs-whatever="
                <img src='${row.img_thumbnail_large.url}'
                width='${row.img_thumbnail_large.width}'
                height='${row.img_thumbnail_large.height}'>
                ">
                ${data} </button>${view_edit}`);
    } else {
        cols += formatColDiv(`<div class="ms-4 mt-2">${data}</div>${view_edit}`);
    }
    // view and edit
    cols += formatColDiv(get_archival(row));
    // specimen context
    cols += formatColDiv(
        row.specimen_context
    )
    // classification
    cols += formatColDiv(row.classification_name)

    // ai_classification
    cols += formatColDiv(row.ai_classification)

    return formatRowDiv(cols)
};

let morphoModal = document.getElementById('morphoModal')
let selectMorphoButton = document.getElementById('morpho-select-btn');
let clearMorphoButton = document.getElementById('morpho-clear-btn');
let recipient = false;
selectMorphoButton.addEventListener('click', function() {
    doMyThing(recipient);
})
clearMorphoButton.addEventListener('click', function() {
    clearSelection(recipient);
})

    let imageModal = document.getElementById('imageModal');

    let jsonDataInput = document.getElementById('id_json_data');
    let submitBtn = document.getElementById('submit-btn');
    let url = json_context.datatables_url
    imageModal.addEventListener('show.bs.modal', event => {
        const button = event.relatedTarget
        const thisimage = button.getAttribute('data-bs-whatever')
        const modalBodyInput = imageModal.querySelector('.modal-body')
        modalBodyInput.innerHTML = thisimage
    })

    function getReviewPanel ( data, type, row ) {
        if (!row.has_image || row.acceptance != 0 || !row.ai_classification_name) {
            /// not applicable to review in these cases
            return ''
        }
        return `<div class="btn-group" role="group" aria-label="Review button group">
<input type="radio" class="btn-check confirm-btn" name="review-${row.id}" id="confirm-${row.id}" value="Confirm" autocomplete="off"/>
<label class="btn btn-outline-success" for="confirm-${row.id}">Confirm</label>
<input type="radio" class="btn-check reject-btn" name="review-${row.id}" id="reject-${row.id}" value="Reject" autocomplete="off"/>
<label class="btn btn-outline-danger" for="reject-${row.id}">Reject</label>
<input type="radio" class="btn-check clear-btn" name="review-${row.id}" id="clear-${row.id}" value="Clear" checked autocomplete="off"/>
<label class="btn btn-link-secondary" for="clear-${row.id}">Clear</label>
</div>
<input class="form-control mt-1" type="text" id="new-class-${row.id}" value="" data-bs-toggle="modal" data-bs-target="#morphoModal" data-bs-whatever="new-class-${row.id}"/>`
    }

    var specimens_table = $('#specimens-table').DataTable({
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
                data: 'img_thumbnail',
                render: getRow
            },
            {
                data: '',
                render: getReviewPanel
            }

        ]
    });

    // reset JsonData when page turn
    specimens_table.on('page', function () {
        resetJsonData()
    });

    // Review Panel buttons
    $('#specimens-table tbody').on('click', '.confirm-btn', function () {
        var row = $(this).closest('tr');

        var id = specimens_table.row( row ).data()["id"];
        json_data.confirm_ids.push(id)
    });
    $('#specimens-table tbody').on('click', '.reject-btn', function () {
        var row = $(this).closest('tr');

        var id = specimens_table.row( row ).data()["id"];
        json_data.reject_ids.push(id)
    });
    $('#specimens-table tbody').on('click', '.clear-btn', function () {
        var row = $(this).closest('tr');
        var id = specimens_table.row( row ).data()["id"];
        var input = document.getElementById(`new-class-${id}`)
        json_data.reject_ids = json_data.reject_ids.filter(v => v !== id)
        json_data.confirm_ids = json_data.confirm_ids.filter(v => v !== id)
        input.value = ''
        delete json_data.new_classifications[id]
    });


    // api_url filters

    let $acceptancePicker = $('<select placeholder="Acceptance (any)" id="acceptance-filter" class="form-select"></select>')
    $('.acceptance-picker').append($acceptancePicker)
    $acceptancePicker.append(`<option value="">Acceptance (any)</option>`)
    $acceptancePicker.append(`<option value="Reviewed">Reviewed</option>`)
    $acceptancePicker.append(json_context.acceptance_choices.map(value => `<option value="${value[0]}">${value[1]}</option>`))
    $acceptancePicker.val('')

    let $archivalCheck = $(`<input class="form-check-input" type="checkbox" value="" id="archivalCheck"><label class="form-check-label ms-1" for="archivalCheck">Archival specimens</label>`)
    $('.archival-check').append($archivalCheck)

    let $userPicker = $(`<select placeholder="User (any)" id="user-filter" class="form-select"></select>`)
    $('.user-picker').append($userPicker)
    $userPicker.append(`<option value="">User (any)</option>`)
    $userPicker.append(json_context.user_choices.map(value => `<option value="${value[0]}">${value[1]}</option>`))
    $userPicker.val('')

    let $countryPicker = $(`<select placeholder="country (any)" id="country-filter" class="form-select"></select>`)
    $('.country-picker').append($countryPicker)
    $countryPicker.append(`<option value="">Country (any)</option>`)
    $countryPicker.append(json_context.country_choices.map(value => `<option value="${value[0]}">${value[1]}</option>`))
    $countryPicker.val('')

    let $statePicker = $(`<select placeholder="State (any)" id="state-filter" class="form-select"></select>`)
    $('.state-picker').append($statePicker)
    $statePicker.append(`<option value="">State (any)</option>`)
    $statePicker.append(usStateChoices.map(value => `<option value="${value[0]}">${value[1]}</option>`))
    $statePicker.val('')

    let $caStatePicker = $(`<select placeholder="State (any)" id="ca-state-filter" class="form-select"></select>`)
    $('.ca-state-picker').append($caStatePicker)
    $caStatePicker.append(`<option value="">State (any)</option>`)
    $caStatePicker.append(caStateChoices.map(value => `<option value="${value[0]}">${value[1]}</option>`))
    $caStatePicker.val('')
    $caStatePicker.hide();

    let $tagPicker = $(`<select placeholder="Tag (any)" id="tag-filter" class="form-select"></select>`)
    $('.tag-picker').append($tagPicker)
    $tagPicker.append(`<option value="">Tag (any)</option>`)
    $tagPicker.append(json_context.tag_choices.map(value => `<option value="${value[0]}">${value[1]}</option>`))
    $tagPicker.val('')

    let $sampleTypePicker = $(`<select placeholder="Sample type (any)" id="sample-type-filter" class="form-select"></select>`)
    $('.sample-type-picker').append($sampleTypePicker)
    $sampleTypePicker.append(`<option value="">Sample type (any)</option>`)
    $sampleTypePicker.append(json_context.sample_type_choices.map(value => `<option value="${value[0]}">${value[1]}</option>`))
    $sampleTypePicker.val('')

    $acceptancePicker.on('change', () => {
        reloadUrl();
    })
    $archivalCheck.on('change', () => {
        reloadUrl();
    })
    $userPicker.on('change', () => {
        reloadUrl();
    })
    // with more countries will need to instead dynamically rebuild select options from STATE_CHOICES.
    $countryPicker.on('change', () => {
        if ($countryPicker.val() == 'CANADA_STATE_CHOICES') {
            $statePicker.hide()
            $statePicker.val('')
            $caStatePicker.show()
        }
        else {
            $caStatePicker.hide()
            $caStatePicker.val('')
            $statePicker.show()
        }
        reloadUrl();
    })
    $statePicker.on('change', () => {
        reloadUrl();
    })
    $tagPicker.on('change', () => {
        reloadUrl();
    })

    $sampleTypePicker.on('change', () => {
        reloadUrl();
    })

    // Review panel

       submitBtn.addEventListener('click', function() {
            jsonDataInput.value = JSON.stringify(json_data);
       })

       let data_table_2 = $('#data-table-2').DataTable({
        order: [[1, 'desc']],
        ordering: false,
        processing: false,
        serverSide: true,
        ajax: {
            url: json_context.datatables_url_2,
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

    $('#data-table-2').on('click', 'tr', function () {
        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected');
        } else {
            data_table_2.$('tr.selected').removeClass('selected');
            $(this).addClass('selected');
        }
    });


    morphoModal.addEventListener('show.bs.modal', event => {
        let button = event.relatedTarget;
        // Set recipient variable
        recipient = button.getAttribute('data-bs-whatever');
    })

    // api_url filters
    let new_datatables_url_2 = ''
    if (json_context.second_picker_choices) {
      let $secondPicker = $('<select placeholder="Filter by" aria-label="Filter by" id="second-picker" class="form-select"></select>')
      $('.second-picker').append($secondPicker)
      $secondPicker.append(`<option value="">` + json_context.second_picker_text + `</option>`)
      $secondPicker.append(json_context.second_picker_choices.map(value => `<option value="${value[0]}">${value[1]}</option>`))
      $secondPicker.val('')
      $secondPicker.on('change', () => {
          new_datatables_url_2 = json_context.datatables_url_2  + '?first_filter=' + $secondPicker.val()
          data_table_2.ajax.url( new_datatables_url_2 ).load();
      })
    };



});

