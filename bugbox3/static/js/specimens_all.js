import $ from 'jquery';
import DataTable from 'datatables.net-bs5';


$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);

let idS = []

let newClassifications = {}



function doMyThing(recipient) {
    if (recipient) {
        let thisRecipient = document.getElementById(recipient);
        let data = data_table_2.rows('.selected').data();
        if (data.length == 1) {
            data = data[0];
            thisRecipient.value = data.name;
            let id = recipient.replace('new-class-', '');
            newClassifications[id] = data.id;
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
        delete newClassifications[id]
    }
}

function formatRowDiv (cols) {
    return `<div class='row'>${cols}</div>`;
}

function formatColDiv (col) {
    return `<div class='col'>${col}</div>`;
}

function getAiReview (row) {
    let disabled = '';
    let confirm_check = '';
    let reject_check = '';
    let clear_check = 'checked';
    let confirmed = '';
    let rejected = '';
    if (!row.has_image || row.acceptance != 0 || !row.ai_classification_name) {
        disabled = 'disabled';
    } else {
        // only can change if acceptance == 0 and has an image
        idS.push(row.id)
    }
    if (row.acceptance == 1) {
        clear_check = '';
        confirm_check = 'checked';
        confirmed = 'ed'
    }
    if (row.acceptance == 2) {
         clear_check = '';
         reject_check = 'checked';
         rejected = 'ed'
    }
    return `<div class="btn-group" role="group" aria-label="Review button group">
<input type="radio" class="btn-check" name="review-${row.id}" id="confirm-${row.id}" value="${row.id}" autocomplete="off" ${confirm_check} ${disabled}>
<label class="btn btn-outline-success" for="confirm-${row.id}">Confirm${confirmed}</label>
<input type="radio" class="btn-check" name="review-${row.id}" id="reject-${row.id}" value="${row.id}" autocomplete="off" ${reject_check} ${disabled}>
<label class="btn btn-outline-danger" for="reject-${row.id}">Reject${rejected}</label>
<input type="radio" class="btn-check" name="review-${row.id}" id="clear-${row.id}" value="" autocomplete="off" ${clear_check} ${disabled}>
<label class="btn btn-link-secondary" for="clear-${row.id}">Clear</label>
</div><input class="form-control mt-1" type="text" id="new-class-${row.id}" value="" data-bs-toggle="modal" data-bs-target="#morphoModal" data-bs-whatever="new-class-${row.id}" ${disabled}>`
}

function getRow ( data, type, row ) {
    let cols = ''
    // img_thumbnail
    if (row.img_thumbnail_large) {
        cols += formatColDiv(`<button type="button" class="btn" data-bs-toggle="modal"
                data-bs-target="#imageModal"
                data-bs-whatever="
                <img src='${row.img_thumbnail_large.url}'
                width='${row.img_thumbnail_large.width}'
                height='${row.img_thumbnail_large.height}'>
                ">
                ${data} </button>`);
    } else {
        cols += formatColDiv(`<div class="ms-4 mt-2">${data}</div>`);
    }
    // view and edit
    cols += formatColDiv(
        `<p><a href="${row.view_link}" target="_blank"><i class="bi bi-eye"></i></a></p>
<p><a href="${row.edit_link}" target="_blank"><i class="bi bi-pencil"></i></a></p>`);
    // specimen context
    cols += formatColDiv(
        row.specimen_context
    )
    // classification
    cols += formatColDiv(row.classification_name)

    // ai_classification
    cols += formatColDiv(row.ai_classification)

    // ai review pane
    cols += formatColDiv(getAiReview(row))

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

    let acceptancePicker = document.getElementById('acceptancePicker');
    let imageModal = document.getElementById('imageModal');
    let json_data = json_context.json_data;
    let jsonDataInput = document.getElementById('id_json_data');
    let submitBtn = document.getElementById('submit-btn');
    let url = json_context.datatables_url + '?acceptance_filter=0'
    imageModal.addEventListener('show.bs.modal', event => {
        const button = event.relatedTarget
        const thisimage = button.getAttribute('data-bs-whatever')
        const modalBodyInput = imageModal.querySelector('.modal-body')
        modalBodyInput.innerHTML = thisimage
    })

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
            }
        ]
    });

     // api_url filters

     acceptancePicker.addEventListener("change", function () {
        url = json_context.datatables_url
        // Allow to add additional query_params and combine with &
        let query_params = []
        if (acceptancePicker.value in [0, 1, 2]) {
            query_params.push(['acceptance_filter', acceptancePicker.value]);
        }
        if (query_params.length) {
            for (let i = 0; i < query_params.length; i++) {
                if (i == 0) {
                    url += '?' + query_params[i][0] + '=' + query_params[i][1];
                } else {
                    url += '&' + query_params[i][0] + '=' + query_params[i][1];
                };
            };

        };
        specimens_table.ajax.url(url).load();
     })

       submitBtn.addEventListener('click', function() {
            for (let i = 0; i < idS.length; i++) {

                let btnConfirm = document.getElementById('confirm-' + idS[i].toString())
                let btnReject = document.getElementById('reject-' + idS[i].toString())
                if (btnConfirm.checked) {
                    json_data.confirm_ids.push(btnConfirm.value)
                } else if (btnReject.checked) {
                    json_data.reject_ids.push(btnReject.value)
                }
                let new_input = document.getElementById('new-class-' + idS[i].toString())
            }
            // overwrite new_classifications
            json_data.new_classifications = newClassifications

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

