import $ from 'jquery';
import DataTable from 'datatables.net-bs5';
import { Modal } from 'bootstrap';

let messageModalBody = document.getElementById('messageModal-body');
let messageModal = new Modal(document.getElementById('messageModal'), {
    keyboard: false
  })

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
    })
    .catch(error => {
        messageModalBody.innerHTML = '<p>' + JSON.stringify(error) + '</p>';
        messageModal.show();
    });
}

$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent)

    function getPanormaSrc(data, type, row) {
        let filename = getFilename(data)
        if (filename) {
            let result = `<a href="${json_context.STITCHER_URL}`
            let s = String(data).replace('media', 'static')
            result += `${s}">${filename}</a>`;
            return result
        } else {
            return 'no panorma available'
        }
    };

    var stitcher_table = $('#stitcher-table').DataTable({
        order: [[1, 'desc']],
        ordering: false,
        processing: true,
        serverSide: true,
        ajax: {
            url: json_context.STITCHER_URL + '/uploads',
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
            },{
                data: 'panorama_path',
                render: getPanormaSrc
            },{
                data: 'guid',
                render: getFormButton
            },
            {
                data: 'approved',
                render: getApproved
            }
        ]
    })

    $('#stitcher-table', 'body').on('click', '.stitcher-form-button', function () {
        var guid = $(this).data('row-id');
        window.location.href = `/core/stitcher-form/${guid}`;
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
        $(this).prop('disabled', true)
        const fileInput = $('#formFile')[0];
        const selectedFile = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', selectedFile);
        const confidence = $('#formConfidence')[0]
        formData.append('confidence_threshold', confidence.value)
        sendZipFile(formData, json_context.STITCHER_URL + '/upload-zip-images')

    })


})
