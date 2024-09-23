import $ from 'jquery';
import DataTable from 'datatables.net-bs5';

$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);
    let jsonDataInput = document.getElementById('id_json_data');
    let submitBtn = document.getElementById('submit-btn');
    let selectAllBtn = document.getElementById('select-all-btn');
    let deleteSpecimensModal = document.getElementById('deleteSpecimensModal');
    let json_data = {ids: []}
    deleteSpecimensModal.addEventListener('show.bs.modal', event => {
        let datalen = st.rows('.selected').data().length;
        const modalBodyInput = deleteSpecimensModal.querySelector('.modal-body')
        if (datalen) {
            modalBodyInput.innerHTML = `Are you sure you want to delete ${datalen} records?`
        } else { modalBodyInput.innerHTML = 'No specimens were selected to delete.' }

    })


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

   selectAllBtn.addEventListener('click', function() {
        if ($('#specimens-table tbody tr').hasClass('selected')) {
            $('#specimens-table tbody tr').removeClass('selected');
        } else {
            $('#specimens-table tbody tr').addClass('selected');
        }
   })


})
