import $ from 'jquery';
import DataTable from 'datatables.net-bs5';
import { Tooltip} from 'bootstrap'

$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new Tooltip(tooltipTriggerEl))
    let jsonDataInput = document.getElementById('id_json_data');
    let selectAllBtn = document.getElementById('select-all-btn');
    let submitBtn = document.getElementById('submit-btn');
    let deleteImagesModal = document.getElementById('deleteImagesModal');
    let json_data = {ids: []};
    let jsonCropDataInput = document.getElementById('id_json_crop_ids');
    let json_crop_ids = {ids: []};
    let cropSubmitBtn = document.getElementById('crop-submit-btn');
    let cropImagesModal = document.getElementById('cropImagesModal');



    let dt = new DataTable('#images-table', {
        order: [[1, 'desc']],
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
            {data: null, orderable: false, searchable: false, className:'select-checkbox', defaultContent: '',},
            {
                data: 'data_row',
            }
        ]
    });

    $('#images-table tbody').on( 'click', 'tr', function () {
        $(this).toggleClass('selected');
    } );

    deleteImagesModal.addEventListener('show.bs.modal', event => {
        let datalen = dt.rows('.selected').data().length;
        const modalBodyInput = deleteImagesModal.querySelector('.modal-body')
        if (datalen) {
            modalBodyInput.innerHTML = `Are you sure you want to delete ${datalen} records? Note: Images with Cropped to specimen set to True will not delete.`
        } else { modalBodyInput.innerHTML = 'No images were selected to delete.' }

    });

    cropImagesModal.addEventListener('show.bs.modal', event => {
        let datalen = dt.rows('.selected').data().length;
        const modalBodyInput = cropImagesModal.querySelector('.modal-body')
        if (datalen) {
            modalBodyInput.innerHTML = `Are you sure you want to crop and save ${datalen} records?`
        } else { modalBodyInput.innerHTML = 'No images were selected to crop.' }
    });

    submitBtn.addEventListener('click', function() {
        let data = dt.rows('.selected').data();
        let ids = []
        if (data.length) {
            for (var i = 0; i < data.length; i++) {
                ids.push(data[i].id)
            }
        }
        json_data.ids = ids
        jsonDataInput.value = JSON.stringify(json_data);
   })

   cropSubmitBtn.addEventListener('click', function() {
    let data = dt.rows('.selected').data();
    let ids = []
    if (data.length) {
        for (var i = 0; i < data.length; i++) {
            ids.push(data[i].id)
        }
    }
    if (json_crop_ids.ids.length == 0) {
        json_crop_ids.ids = ids
        jsonCropDataInput.value = JSON.stringify(json_crop_ids);
    } else {
        $(this).prop("disabled",true);
    }
    })

   selectAllBtn.addEventListener('click', function() {
    if ($('#images-table tbody tr').hasClass('selected')) {
        $('#images-table tbody tr').removeClass('selected');
    } else {
        $('#images-table tbody tr').addClass('selected');
    }
})

})
