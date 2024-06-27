import $ from 'jquery';
import DataTable from 'datatables.net-bs5';

$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);
    let needsClassification = document.getElementById('needsClassification');
    let filterButton = document.getElementById('filterButton');
    let acceptancePicker = document.getElementById('acceptancePicker');
    let imageModal = document.getElementById('imageModal');
    imageModal.addEventListener('show.bs.modal', event => {
        // Button that triggered the modal
        console.log(event.relatedTarget)
        const button = event.relatedTarget
        // Extract info from data-bs-* attributes
        const thisimage = button.getAttribute('data-bs-whatever')
         console.log(thisimage)
        // If necessary, you could initiate an AJAX request here
        // and then do the updating in a callback.
        //
        // Update the modal's content.
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
                render: function (data, type, row, meta) {
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
            console.log('it is checked')
            query_params.push(['acceptance_filter', true]);
        }
        if (acceptancePicker.value in [0, 1, 2]) {
            query_params.push(['first_filter', acceptancePicker.value]);
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
});

