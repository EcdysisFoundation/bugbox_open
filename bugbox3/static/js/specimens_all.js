import $ from 'jquery';
import DataTable from 'datatables.net-bs5';

let idS = []

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
</div>`
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

$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);
    let needsClassification = document.getElementById('needsClassification');
    let filterButton = document.getElementById('filterButton');
    let acceptancePicker = document.getElementById('acceptancePicker');
    let imageModal = document.getElementById('imageModal');
    let json_data = json_context.json_data;
    let jsonDataInput = document.getElementById('id_json_data');
    let submitBtn = document.getElementById('submit-btn');
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
            url: json_context.datatables_url,
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
        if (acceptancePicker.value in [0, 1]) {
            needsClassification.disabled = true
            needsClassification.checked = false;
           } else {
            needsClassification.disabled = false;
           }
     })

     filterButton.addEventListener("click", function() {
        let url = json_context.datatables_url
        let query_params = []

        if (needsClassification.checked) {
            query_params.push(['class_filter', true]);
        }
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
            //alert(idS)
            for (let i = 0; i < idS.length; i++) {
                let btnConfirm = document.getElementById('confirm-' + idS[i].toString())
                let btnReject = document.getElementById('reject-' + idS[i].toString())
                if (btnConfirm.checked) {
                    json_data.confirm_ids.push(btnConfirm.value)
                } else if (btnReject.checked) {
                    json_data.reject_ids.push(btnReject.value)
                }
            }

            jsonDataInput.value = JSON.stringify(json_data);
       })
});

