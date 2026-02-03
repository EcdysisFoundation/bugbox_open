import $ from 'jquery';
import DataTable from 'datatables.net-bs5';

import Uppy from '@uppy/core';
import Dashboard from '@uppy/dashboard';
import XHRUpload from '@uppy/xhr-upload';


$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);
    let jsonDataInput = document.getElementById('id_json_data');
    let moveJsonDataInput = document.getElementById('id_move_json_data');
    let submitBtn = document.getElementById('submit-btn');
    let moveSubmitBtn = document.getElementById('move-submit-btn');
    let selectAllBtn = document.getElementById('select-all-btn');
    let deleteSpecimensModal = document.getElementById('deleteSpecimensModal');
    let moveSpecimensModal = document.getElementById('moveSpecimensModal');
    let classifyAllBtn = document.getElementById('classify-all');
    let json_data = {ids: []};
    let move_json_data = {move_ids:[], move_sample_id: null};
    if (deleteSpecimensModal) {
        deleteSpecimensModal.addEventListener('show.bs.modal', event => {
            let datalen = st.rows('.selected').data().length;
            const modalBodyInput = deleteSpecimensModal.querySelector('.modal-body')
            if (datalen) {
                modalBodyInput.innerHTML = `Are you sure you want to delete ${datalen} records?`
            } else { modalBodyInput.innerHTML = 'No specimens were selected to delete.' }

        });
    }
    if (moveSpecimensModal) {
        moveSpecimensModal.addEventListener('show.bs.modal', event => {
            let datalen = st.rows('.selected').data().length;
            const modalHeaderInput = moveSpecimensModal.querySelector('.modal-header')
            if (datalen) {
                modalHeaderInput.innerHTML = `Select a sample to move ${datalen} selected specimens.`
            } else { modalHeaderInput.innerHTML = 'No specimens were selected to move.' }
        });
    }

    let st = new DataTable('#specimens-table', {
        order: [[1, 'desc']],
        ordering: false,
        processing: false,
        serverSide: true,
        ajax: {
            url: json_context.specimen_datatables_url,
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

    $('#specimens-table tbody').on( 'click', 'tr', function (event) {
        if ($(event.target).closest('td.select-checkbox').length) {
            $(this).toggleClass('selected');
        }
    } );

    if (submitBtn) {
        submitBtn.addEventListener('click', function() {
            let data = st.rows('.selected').data();
            let ids = []
            if (data.length) {
                for (var i = 0; i < data.length; i++) {
                    ids.push(data[i].specimen_id)
                }
            }
            json_data.ids = ids
            if (jsonDataInput) {
                jsonDataInput.value = JSON.stringify(json_data);
            }
       })
    }

    if (moveSubmitBtn) {
        moveSubmitBtn.addEventListener('click', function() {
            let data = st.rows('.selected').data();
            let se_id = sample_table.rows('.selected').data();
            let ids = []
            if (data.length) {
                for (var i = 0; i < data.length; i++) {
                    ids.push(data[i].specimen_id)
                }
            }
            move_json_data.move_ids = ids
            if (se_id.length > 0) {
                move_json_data.move_sample_id = se_id[0].sample_id
            }
            if (moveJsonDataInput) {
                moveJsonDataInput.value = JSON.stringify(move_json_data);
            }
       })
    }

    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function() {
            if ($('#specimens-table tbody tr').hasClass('selected')) {
                $('#specimens-table tbody tr').removeClass('selected');
            } else {
                $('#specimens-table tbody tr').addClass('selected');
            }
       })
    }

    if (classifyAllBtn) {
        classifyAllBtn.addEventListener('click', function() {
            $(this).addClass("disabled")
       })
    }

   let sample_table = null;
   if (document.getElementById('dtsample-table')) {
        sample_table = new DataTable('#dtsample-table', {
            order: [[1, 'desc']],
            ordering: false,
            processing: true,
            serverSide: true,
            ajax: {
                url: json_context.samples_datatables_url,
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

        $('#dtsample-table').on('click', 'tr', function () {
            if ($(this).hasClass('selected')) {
                $(this).removeClass('selected');
            } else {
                sample_table.$('tr.selected').removeClass('selected');
                $(this).addClass('selected');
            }
        });
    }

    // api_url fiters
    let new_datatables_url = ''
    if (json_context.experiment_choices) {
        let $experimentPicker = $('<select placeholder="Filter by" aria-label="Filter by" id="experiment-picker" class="form-select"></select>')
        $('.experiment-picker').append($experimentPicker)
        $experimentPicker.append(`<option value="${json_context.samples_datatables_url}">${json_context.experiment_name}</option>`)
        $experimentPicker.append(json_context.experiment_choices.map(value => `<option value="${value[0]}">${value[1]}</option>`))
        $experimentPicker.val(json_context.samples_datatables_url)
        $experimentPicker.on('change', () => {
            new_datatables_url = $experimentPicker.val()
            sample_table.ajax.url( new_datatables_url ).load();
        })
    }

    // UPPY
    if (document.getElementById('uppyImagesUpload') && json_context.image_upload_url) {
        const uppy = new Uppy().use(Dashboard, {
            trigger: '#uppyImagesUpload',
            doneButtonHandler: () => {
                location.reload()
            }
        })
        uppy.use(XHRUpload, {
            endpoint: json_context.image_upload_url,
            formData: true,
            fieldName: 'image',
          })
        if (json_context.csrf_token) {
            uppy.setMeta({ csrfmiddlewaretoken: json_context.csrf_token });
        }
    }
})
