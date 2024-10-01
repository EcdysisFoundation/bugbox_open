import $ from 'jquery';
import DataTable from 'datatables.net-bs5';

$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);
    let jsonDataInput = document.getElementById('id_json_data');
    let moveJsonDataInput = document.getElementById('id_move_json_data');
    let submitBtn = document.getElementById('submit-btn');
    let moveSubmitBtn = document.getElementById('move-submit-btn')
    let selectAllBtn = document.getElementById('select-all-btn');
    let deleteSpecimensModal = document.getElementById('deleteSpecimensModal');
    let moveSpecimensModal = document.getElementById('moveSpecimensModal');
    let classifyAllBtn = document.getElementById('classify-all');
    let json_data = {ids: []};
    let move_json_data = {move_ids:[], move_sample_id: null};
    deleteSpecimensModal.addEventListener('show.bs.modal', event => {
        let datalen = st.rows('.selected').data().length;
        const modalBodyInput = deleteSpecimensModal.querySelector('.modal-body')
        if (datalen) {
            modalBodyInput.innerHTML = `Are you sure you want to delete ${datalen} records?`
        } else { modalBodyInput.innerHTML = 'No specimens were selected to delete.' }

    });
    moveSpecimensModal.addEventListener('show.bs.modal', event => {
        let datalen = st.rows('.selected').data().length;
        const modalHeaderInput = moveSpecimensModal.querySelector('.modal-header')
        if (datalen) {
            modalHeaderInput.innerHTML = `Select a sample to move ${datalen} selected specimens.`
        } else { modalHeaderInput.innerHTML = 'No specimens were selected to move.' }
    });

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

    $('#specimens-table tbody').on( 'click', 'tr', function () {
        $(this).toggleClass('selected');
    } );

    submitBtn.addEventListener('click', function() {
        let data = st.rows('.selected').data();
        let ids = []
        if (data.length) {
            for (var i = 0; i < data.length; i++) {
                ids.push(data[i].specimen_id)
            }
        }
        json_data.ids = ids
        jsonDataInput.value = JSON.stringify(json_data);
   })

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
        move_json_data.move_sample_id = se_id[0].sample_id
        moveJsonDataInput.value = JSON.stringify(move_json_data);
   })

   selectAllBtn.addEventListener('click', function() {
        if ($('#specimens-table tbody tr').hasClass('selected')) {
            $('#specimens-table tbody tr').removeClass('selected');
        } else {
            $('#specimens-table tbody tr').addClass('selected');
        }
   })

   classifyAllBtn.addEventListener('click', function() {
        $(this).addClass("disabled")
   })

   let sample_table = new DataTable('#dtsample-table', {
        order: [[1, 'desc']],
        ordering: false,
        processing: false,
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


})
