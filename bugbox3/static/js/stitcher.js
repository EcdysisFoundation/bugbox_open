import $ from 'jquery';
import DataTable from 'datatables.net-bs5';

function getFilename(path) {
  if (path) {
    const lastSlashIndex = path.lastIndexOf('/');
    if (lastSlashIndex !== -1) {
      return path.substring(lastSlashIndex + 1);
    }
  }
  return ""; // Return an empty string if the path is invalid or no filename is found
}

function getPanormaSrc(data, type, row) {
    let filename = getFilename(data)
    if (filename) {
        let result = `<a href="http://localhost:8090`
        let s = String(data).replace('media', 'static')
        result += `${s}">${filename}</a>`;
        console.log(result)
        return result
    } else {
        return 'no panorma available'
    }
};

$(function () {
    //const json_context = JSON.parse(document.getElementById('json_context').textContent)
    var stitcher_table = $('#stitcher-table').DataTable({
        order: [[1, 'desc']],
        ordering: false,
        processing: true,
        serverSide: true,
        ajax: {
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
            }
        ]
    })

})
