import $ from 'jquery';
import { Modal } from 'bootstrap';

let messageModalBody = document.getElementById('messageModal-body');
let messageModal = new Modal(document.getElementById('messageModal'), {
    keyboard: false
  })

function updateStitching( url ) {
    $.post(url).done(function( data ) {
    messageModalBody.innerHTML = '<p>' + data.message +
'</p><p>Processing may take a few minutes to complete.</p>';
    messageModal.show();
}).fail(function( data, status, error ) {
    messageModalBody.innerHTML = '<p>'+ JSON.stringify(data) + status + ' ' + error +
    '</p><p>Update Failed.</p>';
    messageModal.show();
})}


$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent)

    let $confidenceInput = $('<input type="number" step="0.1" id="formConfidence" class="form-control" value="0.6" max="0.9" min="0.1" required="true">')
    $('.confidence-input').append($confidenceInput)

    let $stitchButton = $('<button class="btn btn-warning mb-3 mt-2 text-nowrap" type="button">Update Stitching</button>')
    if ( json_context.disable_stitching ) {
        $stitchButton.prop('disabled', true);
    }
    $('.stitch-button').append($stitchButton)
    $stitchButton.on('click', function() {
        const confidence = $confidenceInput[0].value
        const params = `?guid=${json_context.guid}&confidence_threshold=${confidence}`
        $(this).prop('disabled', true);
        updateStitching(
            json_context.STITCHER_URL + '/update-stitching/' + params)
    });

    let $deleteButton = $(`<a href="${json_context.stitcher_delete_url}" class="btn btn-danger mb-3 mt-2 text-nowrap" type="button">Delete</a>`)
    console.log(json_context.disable_delete)
    if ( json_context.disable_delete ) {
        $deleteButton.addClass('disabled');
    }
    $('.delete-button').append($deleteButton)

})
