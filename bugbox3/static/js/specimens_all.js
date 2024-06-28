import $ from 'jquery';
import DataTable from 'datatables.net-bs5';

$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);
    let needsClassification = document.getElementById('needsClassification');
    let filterButton = document.getElementById('filterButton');
    let acceptancePicker = document.getElementById('acceptancePicker');
    let imageModal = document.getElementById('imageModal');
    let json_data = json_context.json_data;
    let jsonDataInput = document.getElementById('id_json_data');
    let submitBtn = document.getElementById('submit-btn');
    let idS = []
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
                render: function (data, type, row) {
                    if (row.img_thumbnail_large) {
                        return `<button type="button" class="btn" data-bs-toggle="modal"
                                data-bs-target="#imageModal"
                                data-bs-whatever="
                                <img src='${row.img_thumbnail_large.url}'
                                width='${row.img_thumbnail_large.width}'
                                height='${row.img_thumbnail_large.height}'>
                                ">
                                ${data} </button>`
                    } else {
                        return `<div class="ms-4 mt-2">${data}</div>`
                    }

                }
            },
            {
                data: 'data_row',
            },
            {
                data: 'id',
                render: function (data, type, row) {
                    idS.push(data)
                    let disabled = ''
                    if (!row.has_image) {
                        disabled = 'disabled'
                    }
                    return `<div class="btn-group" role="group" aria-label="Review button group">
<input type="radio" class="btn-check" name="review-${data}" id="confirm-${data}" value="${data}" autocomplete="off" ${disabled}>
<label class="btn btn-outline-success" for="confirm-${data}">Confirm</label>
<input type="radio" class="btn-check" name="review-${data}" id="reject-${data}" value="${data}" autocomplete="off" ${disabled}>
<label class="btn btn-outline-danger" for="reject-${data}">Reject</label>
<input type="radio" class="btn-check" name="review-${data}" id="clear-${data}" value="" autocomplete="off" checked ${disabled}>
<label class="btn btn-link-secondary" for="clear-${data}">Clear</label>
</div>`
                }
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
                } else {
                    if (btnReject.checked) {
                        json_data.reject_ids.push(btnReject.value)
                    }
                }
            }

            jsonDataInput.value = JSON.stringify(json_data);
       })
});

