import $ from 'jquery';
import DataTable from 'datatables.net-bs5';
import { Modal } from 'bootstrap';

let messageModalBody = document.getElementById('messageModal-body');
let messageModal = new Modal(document.getElementById('messageModal'), {
    keyboard: false
  })


function getUrl(dt_url, data_filters) {

    let url_args = '';
    let sep = '?';
    if (data_filters.ls_project) {
        // more sanitation required if view not on private network
        let cleaned_val = encodeURIComponent(data_filters.ls_project)
        url_args = `${sep}lsproject=${cleaned_val}`
        sep = '&'
    };
    // true false filters
    url_args += `${sep}unreviewed=${data_filters.unreviewed}`;
    if (sep == '?') {sep = '&'}; // there is at least one arg here
    url_args += `${sep}approved=${data_filters.approved}`;
    url_args += `${sep}disapproved=${data_filters.disapproved}`;

    return `${dt_url}/uploads${url_args}`
}

function getFilename(path) {
  if (path) {
    const lastSlashIndex = path.lastIndexOf('/');
    if (lastSlashIndex !== -1) {
      return path.substring(lastSlashIndex + 1);
    }
  }
  return '';
}

function getFormButton(data) {
    var buttonId = 'actionButton_' + data; // Assuming `row.id` is unique
    return `<button id="${buttonId}" class="btn btn-primary stitcher-form-button" data-row-id="${data}">-></button>`;
}

function getApproved(approved) {
    if (approved == null) {
        return approved
    }
    if (approved) {
        return 'Approved'
    }
    if (!approved) {
            return 'Disapproved'
        }
    return approved
}

function sendZipFile(formData, api_url) {
    fetch(api_url, {
        method: 'POST',
        body: formData // The FormData object automatically sets the 'Content-Type' header to 'multipart/form-data'
    })
    .then(response => response.json()) // Parse the JSON response from the API
    .then(data => {
        messageModalBody.innerHTML = '<p>' + JSON.stringify(data) + '</p>';
        messageModal.show();
        $('#formFile').val('');
    })
    .catch(error => {
        messageModalBody.innerHTML = '<p>' + JSON.stringify(error) + '</p>';
        messageModal.show();
        $('#formFile').val('');
    });
}

function getSampleUrl(data) {
    if (data) {
        return `<a href="/samples/sample/${data}" target="_blank">${data}</a>`
    } else { return '' }
}

function concatTen(data) {
    if (data) {
        return String(data).slice(0, 10)
    } else { return '' }
}

function getSent(data) {
    if (data) {
        return '<i class="bi bi-send-check-fill h4 text-success"></i>'
    } else { return '' }
}


$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent)
    // take this out, just keep up with vars in functions verbose
    let data_filters = {
        ls_project: '',
        unreviewed: true,
        approved: true,
        disapproved: false
    }

    let $confidenceInput = $('<input type="number" step="0.1" id="formConfidence" class="form-control" value="0.6" max="0.9" min="0.1" required="true">')
    $('.confidence-input').append($confidenceInput)

    function getPanoramaSrc(data, type, row) {
        let filename = getFilename(data)
        if (filename) {
            let result = `<a href="${json_context.STITCHER_URL}`
            let s = String(data).replace('media', 'static')
            result += `${s}" target="_blank">${filename}</a>`;
            return result
        } else {
            return 'no panorama available'
        }
    };

    var stitcher_table = $('#stitcher-table').DataTable({
        order: [[1, 'desc']],
        ordering: false,
        processing: true,
        serverSide: true,
        ajax: {
            url: getUrl(json_context.STITCHER_URL, data_filters),
            dataSrc: 'data'
        },
        language: {
            searchPlaceholder: "Search"
        },
        columns: [
            {
                data: 'upload_dir_name',
            },{
                data: 'guid',
                render: getFormButton
            },{
                data: 'panorama_path',
                render: getPanoramaSrc
            },{
                data: 'bugbox_sample_id',
                render: getSampleUrl
            },{
                data: 'approved',
                render: getApproved
            },{
                data: 'label_studio_project'
            },{
                data: 'predictions_timestamp_coco',
                render: concatTen
            },{
                data: 'annotations_updated_at_segment',
                render: concatTen
            },{
                data: 'bugbox_croped_saved',
                render: getSent
            }
        ]
    })

    $('#stitcher-table', 'body').on('click', '.stitcher-form-button', function () {
        var guid = $(this).data('row-id');
        window.open(`/core/stitcher-form/${guid}`, '_blank');
        })


    $('#formFile').on('change', function() {
        if ($(this).val()) {
        $uploadButton.removeAttr('disabled');
        } else {
        $uploadButton.attr('disabled', 'disabled');
        }
    });

    let $uploadButton = $('<button class="btn btn-warning mb-3 mt-2 text-nowrap" type="button" disabled>Upload Zip File</button>')
    $('.upload-button').append($uploadButton)
    $uploadButton.on('click', function() {
        $(this).prop('disabled', true);
        const fileInput = $('#formFile')[0];
        const selectedFile = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', selectedFile);
        const confidence = $confidenceInput[0].value
        formData.append('confidence_threshold', confidence)
        const params = `?confidence_threshold=${confidence}`
        sendZipFile(formData, json_context.STITCHER_URL + '/upload-zip-images/' + params)
    });

    // api_url filters
    let new_datatables_url = '';
    let $lsProjectPicker = $('<select placeholder="Filter by" aria-label="Filter by" id="approved-picker" class="form-select"></select>')
        $('.label-studio-picker').append($lsProjectPicker)
        $lsProjectPicker.append(`<option value="">` + 'LS Projects' + `</option>`)
        $lsProjectPicker.append(json_context.ls_projects_choices.map(value => `<option value="${value[0]}">${value[1]}</option>`))
        $lsProjectPicker.val('')

    $lsProjectPicker.on('change', () => {
        data_filters.ls_project = $lsProjectPicker.val()
        new_datatables_url = getUrl(json_context.STITCHER_URL, data_filters)
        stitcher_table.ajax.url( new_datatables_url ).load();
    })

    let unreviewed_check = '';
    if (data_filters.unreviewed) {
        unreviewed_check = 'checked';
    };
    let $unreviewedCheck = $(`<input class="form-check-input" type="checkbox" value="" id="unreviewedCheck" ${unreviewed_check}>`)
    $('.unreviewed-check').append($unreviewedCheck)

    $unreviewedCheck.on('change', () => {
        data_filters.unreviewed = $unreviewedCheck.prop("checked");
        new_datatables_url = getUrl(json_context.STITCHER_URL, data_filters);
        stitcher_table.ajax.url( new_datatables_url ).load();
    })

    let approved_check = '';
    if (data_filters.approved) {
        approved_check = 'checked';
    };
    let $approvedCheck = $(`<input class="form-check-input" type="checkbox" value="" id="approvedCheck" ${approved_check}>`)
    $('.approved-check').append($approvedCheck)

    $approvedCheck.on('change', () => {
        data_filters.approved = $approvedCheck.prop("checked");
        new_datatables_url = getUrl(json_context.STITCHER_URL, data_filters);
        stitcher_table.ajax.url( new_datatables_url ).load();
    })

    let disapprove_check = '';
    if (data_filters.disapprove) {
        disapprove_check = 'checked';
    };
    let $disapprovedCheck = $(`<input class="form-check-input" type="checkbox" value="" id="disapprovedCheck" ${disapprove_check}>`)
    $('.disapproved-check').append($disapprovedCheck)

    $disapprovedCheck.on('change', () => {
        data_filters.disapproved = $disapprovedCheck.prop("checked");
        new_datatables_url = getUrl(json_context.STITCHER_URL, data_filters);
        stitcher_table.ajax.url( new_datatables_url ).load();
    })


})
