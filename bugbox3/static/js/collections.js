import $ from 'jquery';
import DataTable from 'datatables.net-bs5';

function getDescription(data, type, row) {
    return `
<ul class="list-group list-group-flush">
  <li class="list-group-item"><b>Order:</b> ${row.taxonomy.gbif_order}</li>
  <li class="list-group-item"><b>Family:</b> ${row.taxonomy.gbif_family}</li>
  <li class="list-group-item"><b>Species:</b> <i>${row.taxonomy.species}</i></li>
  <li class="list-group-item">${row.details.visit_date} | ${row.details.location}</li>
  <li class="list-group-item">${row.details.archival}</li>
</ul>
`
}

function getUrl(dt_url, archival_check) {
    let url_str = ''
    let params = []
    if (archival_check.prop("checked")) {
        params.push('archival=' + archival_check.prop("checked"));
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

function getImage ( data, type, row ) {
    let result = ''
    if (row.img_thumbnail_large) {
        result += `<button type="button" class="btn" data-bs-toggle="modal"
                data-bs-target="#imageModal"
                data-bs-whatever="
                <img src='${row.img_thumbnail_large.url}'
                width='${row.img_thumbnail_large.width}'
                height='${row.img_thumbnail_large.height}'>
                ">${data}</button>`;
    } else {
        result += `${data}`;
    }
    return result
};


$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);

    let imageModal = document.getElementById('imageModal');
    imageModal.addEventListener('show.bs.modal', event => {
        const button = event.relatedTarget
        const thisimage = button.getAttribute('data-bs-whatever')
        const modalBodyInput = imageModal.querySelector('.modal-body')
        modalBodyInput.innerHTML = thisimage
    })

    var data_table = $('#data-table').DataTable({
        order: [[1, 'desc']],
        pageLength: 10,
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
                data: 'image',
                render: getImage
            },
            {
                data: '',
                render: getDescription
            }
        ],
        columnDefs: [
            {
                targets: 0,
                className: 'dt-body-right'
            }
        ]
    });

    // api_url filters

    function reloadUrl() {
        data_table.ajax.url( getUrl(
                json_context.datatables_url,
                $archivalCheck
            )).load();
    }

    let $archivalCheck = $(`<input class="form-check-input" type="checkbox" value="" id="archivalCheck"><label class="form-check-label ms-1" for="archivalCheck"><h4>${json_context.collection}</h4></label>`)
    $('.archival-check').append($archivalCheck)

    $archivalCheck.on('change', () => {
        reloadUrl();
    })

});

