import $ from 'jquery';
import DataTable from 'datatables.net-bs5';


$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);
    const FILTER_STORAGE_KEY = 'bugbox_specimens_filters';
    const isAlphaNumeric = str => /^[a-z0-9]*$/gi.test(str);
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
    function cleanInput(usertxt) {
        let result = ''
        for (let i = 0; i < usertxt.length; i++) {
            if (isAlphaNumeric(usertxt[i]) || usertxt[i] == ' ') {
                result += usertxt[i]
            }
        }
        return result
    }


    let usStateChoices = json_context.state_choices_dict.US_STATE_CHOICES
    let caStateChoices = json_context.state_choices_dict.CANADA_STATE_CHOICES

    let isReloading = false;
    let reloadTimeout;
    function delayedReload(ms = 300) {
        clearTimeout(reloadTimeout);
        reloadTimeout = setTimeout(() => reloadUrl(), ms);
    }

    // Load filters from localStorage or setting default values
    function saveFilterState() {
        const filters = {
            acceptance: $acceptancePicker.val(),
            archival: $archivalCheck.prop('checked'),
            user: $userPicker.val(),
            country: $countryPicker.val(),
            state: $statePicker.val(),
            ca_state: $caStatePicker.val(),
            tag: $tagPicker.val(),
            sample_type: $sampleTypePicker.val(),
            recent_year: $recentYearPicker.val(),
            classification: $classificationFilter.val(),
            radio: document.getElementById('classificationRadio').checked ? 'Reviewed' : 'AI'
        };
        localStorage.setItem(FILTER_STORAGE_KEY, JSON.stringify(filters));
    }

    function restoreFilterState() {
        const stored = localStorage.getItem(FILTER_STORAGE_KEY);
        if (!stored) return;
        const filters = JSON.parse(stored);

        $acceptancePicker.val(filters.acceptance || '').trigger('change');
        $archivalCheck.prop('checked', filters.archival || false).trigger('change');
        $userPicker.val(filters.user || '').trigger('change');
        $countryPicker.val(filters.country || '').trigger('change');

        if (filters.country === 'CANADA_STATE_CHOICES') {
            $statePicker.hide();
            $caStatePicker.show().val(filters.ca_state || '').trigger('change');
        } else {
            $caStatePicker.hide();
            $statePicker.show().val(filters.state || '').trigger('change');
        }

        $tagPicker.val(filters.tag || '').trigger('change');
        $sampleTypePicker.val(filters.sample_type || '').trigger('change');
        $recentYearPicker.val(filters.recent_year || '').trigger('change');
        $classificationFilter.val(filters.classification || '');

        if (filters.radio === 'AI') {
            document.getElementById('aiClassificationRadio').checked = true;
        } else {
            document.getElementById('classificationRadio').checked = true;
        }
    }

    function clearAllFilters() {
        // Clear filter values
        $acceptancePicker.val('').trigger('change');
        $archivalCheck.prop('checked', false).trigger('change');
        $userPicker.val('').trigger('change');
        $countryPicker.val('').trigger('change');
        $statePicker.val('').trigger('change');
        $caStatePicker.val('').trigger('change');
        $caStatePicker.hide();
        $statePicker.show();
        $tagPicker.val('').trigger('change');
        $sampleTypePicker.val('').trigger('change');
        $recentYearPicker.val('').trigger('change');
        $classificationFilter.val('');
        document.getElementById('classificationRadio').checked = true;

        // Clear from localStorage
        localStorage.removeItem(FILTER_STORAGE_KEY);

        reloadUrl();
    }

    function getUrl(dt_url,
        acceptance_filter, archival_check, user_filter,
        country_filter, state_filter, tag_filter, sample_type_filter,
        recent_year_filter,
        classification_filter,
        classification_radio,
        ai_classification_radio
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
            params.push('sample_type=' + sample_type_filter);
        }
        if (recent_year_filter) {
            params.push('recent_year=' + recent_year_filter);
        }
        if (classification_filter) {
            let x = cleanInput(classification_filter)
            if (x) {
                params.push('classification_filter=' + x);
            }
        }
        if (classification_radio) {
            params.push('classification_radio=' + classification_radio);
        }
        if (ai_classification_radio) {
            params.push('ai_classification_radio=' + ai_classification_radio);
        }
        for (let i = 0; i < params.length; i++) {
            let sep = '&'
            if (i == 0) {
                sep = '?'
            }
            url_str += `${sep}${params[i]}`;
        }
        return `${dt_url}${url_str}`
    }

    function reloadUrl() {
        if (isReloading) return;
        isReloading = true;
        specimens_table.ajax.url(getUrl(
            json_context.datatables_url,
            $acceptancePicker.val(), $archivalCheck, $userPicker.val(),
            $countryPicker.val(), $statePicker.val(), $tagPicker.val(),
            $sampleTypePicker.val(), $recentYearPicker.val(),
            $classificationFilter.val(),
            document.getElementById('classificationRadio').checked,
            document.getElementById('aiClassificationRadio').checked
        )).load(() => {
            isReloading = false;
        });
        resetJsonData();
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

    function formatRowDiv(cols) {
        return `<div class='row'>${cols}</div>`;
    }

    function formatColDiv(col) {
        return `<div class=\"col\">${col}</div>`;
    }

    function get_archival(row) {
        if (row.archival_identifier) {
            return `${row.archival_identifier}<br/>${row.archival_stored}`
        } else {
            return ''
        }
    }


    function getRow(data, type, row) {
        let cols = ''
        let view_edit = `<h5><a href="${row.view_link}" target="_blank"><i class="bi bi-eye"></i></a>
<a href="${row.edit_link}" target="_blank"><i class="bi bi-pencil"></i></a></h5>`
        // img_thumbnail
        if (row.img_thumbnail_large) {
            let width = row.img_thumbnail_large.width;
            let height = row.img_thumbnail_large.height;

            let widthAttr = width && !isNaN(width) ? `width='${width}'` : '';
            let heightAttr = height && !isNaN(height) ? `height='${height}'` : '';

            cols += formatColDiv(`<button type="button" class="btn" data-bs-toggle="modal"
                data-bs-target="#imageModal"
                data-bs-whatever="
                <img src='${row.img_thumbnail_large.url}' ${widthAttr} ${heightAttr}>
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
        cols += formatColDiv(`${row.classification_name}<br/>${row.gbif_canonical_name}`)

        // ai_classification
        cols += formatColDiv(row.ai_classification)

        return formatRowDiv(cols)
    };

    let morphoModal = document.getElementById('morphoModal')
    let selectMorphoButton = document.getElementById('morpho-select-btn');
    let clearMorphoButton = document.getElementById('morpho-clear-btn');
    let recipient = false;
    selectMorphoButton.addEventListener('click', function () {
        doMyThing(recipient);
    })
    clearMorphoButton.addEventListener('click', function () {
        clearSelection(recipient);
    })

    let imageModal = document.getElementById('imageModal');

    let jsonDataInput = document.getElementById('id_json_data');
    let submitBtn = document.getElementById('submit-btn');
    
    // for testing
    const USE_OPTIMIZED = window.location.search.includes('optimized=true');
    let url = json_context.datatables_url;
    
    if (USE_OPTIMIZED) {
        url = url.replace('specimens-all-data/', 'specimens-all-data-optimized/');
        console.log('* Using optimized endpoint:', url);
    } else {
        console.log('* Using original endpoint:', url);
    }
    imageModal.addEventListener('show.bs.modal', event => {
        const button = event.relatedTarget
        const thisimage = button.getAttribute('data-bs-whatever')
        const modalBodyInput = imageModal.querySelector('.modal-body')
        modalBodyInput.innerHTML = thisimage
    })

    function getReviewPanel(data, type, row) {
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
        pageLength: 100,
        ordering: false,
        processing: true,
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

        var id = specimens_table.row(row).data()["id"];
        json_data.confirm_ids.push(id)
    });
    $('#specimens-table tbody').on('click', '.reject-btn', function () {
        var row = $(this).closest('tr');

        var id = specimens_table.row(row).data()["id"];
        json_data.reject_ids.push(id)
    });
    $('#specimens-table tbody').on('click', '.clear-btn', function () {
        var row = $(this).closest('tr');
        var id = specimens_table.row(row).data()["id"];
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

    let $recentYearPicker = $(`<select placeholder="Year (any)" id="recent-year-filter" class="form-select"></select>`)
    $('.recent-year-picker').append($recentYearPicker)
    $recentYearPicker.append(`<option value="">Year (any)</option>`)
    $recentYearPicker.append(json_context.recent_year_choices.map(value => `<option value="${value[0]}">${value[1]}</option>`))
    $recentYearPicker.val('')

    let $classificationFilter = $(`<input type="text" class="form-control" id="morphospecies-filter" placeholder="Morphospecies (Reviewed / AI)" maxlength="30">`)
    $('.morphospecies-filter').append($classificationFilter)

    let $classificationToggle = $(`<div class="form-check form-check-inline">
        <input class="form-check-input" type="radio" name="inlineRadioOptions" id="classificationRadio" value="Reviewed" checked>
        <label class="form-check-label text-white" for="classificationRadio">Reviewed</label>
        </div>
        <div class="form-check form-check-inline">
        <input class="form-check-input" type="radio" name="inlineRadioOptions" id="aiClassificationRadio" value="AI">
        <label class="form-check-label text-white" for="aiClassificationRadio">AI</label>
        </div>`)
    $('.classification-toggle').append($classificationToggle)

    let $classificationFilterButton = $(`<button type="button" class="btn btn-info">Search</button>`)
    $('.classification-search-btn').append($classificationFilterButton)

    $acceptancePicker.on('change', () => {
        saveFilterState();
        delayedReload();
    })
    $archivalCheck.on('change', () => {
        saveFilterState();
        delayedReload();
    })
    $userPicker.on('change', () => {
        saveFilterState();
        delayedReload();
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
        saveFilterState();
        delayedReload();
    })
    $statePicker.on('change', () => {
        saveFilterState();
        delayedReload();
    })
    $tagPicker.on('change', () => {
        saveFilterState();
        delayedReload();
    })
    $sampleTypePicker.on('change', () => {
        saveFilterState();
        delayedReload();
    })
    $recentYearPicker.on('change', () => {
        saveFilterState();
        delayedReload();
    })
    $classificationFilterButton.on('click', () => {
        saveFilterState();
        delayedReload();
    })
    $('#classificationRadio, #aiClassificationRadio').on('change', () => {
        saveFilterState();
        delayedReload();
    });
    // organization picker
    let $orgPicker = $(`<select placeholder="Organization" id="org-filter" class="form-select"></select>`)
    $('.org-picker').append($orgPicker)
    $orgPicker.append(json_context.org_choices.map(value => `<option value="${value[0]}">${value[1]}</option>`))
    $orgPicker.val(json_context.org_choices[0][0])
    $orgPicker.on('change', () => {
        let theLink = ''
        for (var i = 0; i < json_context.org_choices.length; i++) {
            if (json_context.org_choices[i][0] == String($orgPicker.val())) {
                theLink = json_context.org_choices[i][2]
                window.location.replace(theLink)
                break;
            }
        }
    })

    // Review panel

    submitBtn.addEventListener('click', function () {
        jsonDataInput.value = JSON.stringify(json_data);
    })

    let data_table_2 = $('#data-table-2').DataTable({
        order: [[1, 'desc']],
        ordering: false,
        processing: true,
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
            new_datatables_url_2 = json_context.datatables_url_2 + '?first_filter=' + $secondPicker.val()
            data_table_2.ajax.url(new_datatables_url_2).load();
        })
    };

    // Restore filter state from localStorage
    restoreFilterState();
    $('#clearFiltersBtn').on('click', clearAllFilters);
    delayedReload();

});

