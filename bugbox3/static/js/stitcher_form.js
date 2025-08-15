import $ from 'jquery';
import { Modal } from 'bootstrap';

let messageModalBody = document.getElementById('messageModal-body');
let messageModal = new Modal(document.getElementById('messageModal'), {
    keyboard: false
  })

function updateStitching( url ) { $.post(url, function( data ) {
}).done(function( data ) {
    messageModalBody.innerHTML = '<p>' + data.message +
'</p><p>Processing may take a few minutes to complete.</p>';
    messageModal.show();
}).fail(function( data ) {
    messageModalBody.innerHTML = '<p>' + data +
    '</p><p>Update Failed.</p>';
    messageModal.show();
})}

$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent)
    let $stitchButton = $('<button class="btn btn-warning mb-3 mt-2 text-nowrap" type="button">Update Stitching</button>')
    if ( json_context.disable_stitching ) {
        $stitchButton.prop('disabled', true);
    }
    $('.stitch-button').append($stitchButton)
    $stitchButton.on('click', function() {
        updateStitching(
            json_context.STITCHER_URL + '/update-stitching?guid=' + json_context.guid)
            $(this).prop('disabled', true);
    });
})
