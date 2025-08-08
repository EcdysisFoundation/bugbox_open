import $ from 'jquery';
import DataTable from 'datatables.net-bs5';

function getFilename(path) {
  if (path) {
    const lastSlashIndex = path.lastIndexOf('/');
    if (lastSlashIndex !== -1) {
      return path.substring(lastSlashIndex + 1);
    }
  }
  return '';
}

function getPanormaSrc(data, type, row) {
    let filename = getFilename(data)
    if (filename) {
        // let result = `<a href="${json_context.STITCHER_URL}`
        let result = `<a href="http://localhost:8090`
        let s = String(data).replace('media', 'static')
        result += `${s}">${filename}</a>`;
        //console.log(result)
        return result
    } else {
        return 'no panorma available'
    }
};

function getFormButton(data) {
    var buttonId = 'actionButton_' + data; // Assuming `row.id` is unique
    return `<button id="${buttonId}" class="btn btn-primary stitcher-form-button" data-row-id="${data}">-></button>`;
}

$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent)
    var stitcher_table = $('#stitcher-table').DataTable({
        order: [[1, 'desc']],
        ordering: false,
        processing: true,
        serverSide: true,
        ajax: {
            // url: json_context.STITCHER_URL + '/uploads',
            url: 'http://localhost:8090/uploads',
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
            }
        ]
    })

    $('#stitcher-table', 'body').on('click', '.stitcher-form-button', function () {
        var guid = $(this).data('row-id');
        window.open(`/core/stitcher-form/${guid}`, "_blank");
        })

})
