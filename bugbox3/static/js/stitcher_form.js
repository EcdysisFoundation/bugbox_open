import $ from 'jquery';
import { Modal } from 'bootstrap';

let messageModalBody = document.getElementById('messageModal-body');
let messageModal = new Modal(document.getElementById('messageModal'), {
    keyboard: false
  })

const STORAGE_KEY_PREFIX = 'stitcher_confidence_';
const POLL_INTERVAL_MS = 4500;
const POLL_TIMEOUT_MS = 5 * 60 * 1000;

function updateStitching(url, opts) {
    const { panoramaStatusUrl, initialTimestamp, initialPath } = opts || {};
    $.post(url).done(function (data) {
        const msg = (data && data.message) ? data.message : 'Update started.';
        messageModalBody.innerHTML = '<p>' + msg +
            '</p><p>Processing may take a few minutes to complete.</p>';
        messageModal.show();
        if (panoramaStatusUrl != null) {
            startPollingForNewImage(panoramaStatusUrl, initialTimestamp, initialPath);
        }
    }).fail(function (data, status, error) {
        messageModalBody.innerHTML = '<p>' + JSON.stringify(data) + status + ' ' + error +
            '</p><p>Update Failed.</p>';
        messageModal.show();
    });
}

function startPollingForNewImage(panoramaStatusUrl, initialTimestamp, initialPath) {
    const startTime = Date.now();
    const poll = function () {
        if (Date.now() - startTime > POLL_TIMEOUT_MS) {
            $('.stitch-button button').prop('disabled', false);
            if (messageModalBody) {
                messageModalBody.innerHTML += '<p><em>If the image has not updated, refresh the page.</em></p>';
            }
            return;
        }
        $.getJSON(panoramaStatusUrl).done(function (data) {
            const ts = data.panorama_timestamp;
            const path = data.panorama_path;
            const timestampChanged = ts != null && String(ts) !== String(initialTimestamp);
            const pathChanged = path != null && path !== initialPath;
            if (timestampChanged || pathChanged) {
                location.reload();
                return;
            }
            setTimeout(poll, POLL_INTERVAL_MS);
        }).fail(function () {
            setTimeout(poll, POLL_INTERVAL_MS);
        });
    };
    setTimeout(poll, POLL_INTERVAL_MS);
}


$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent)

    const confidenceStorageKey = STORAGE_KEY_PREFIX + json_context.guid;
    const defaultConfidence = (
        localStorage.getItem(confidenceStorageKey) ||
        (json_context.panorama_confidence != null ? String(json_context.panorama_confidence) : null) ||
        '0.6'
    );
    let $confidenceInput = $('<input type="number" step="0.1" id="formConfidence" class="form-control" max="0.9" min="0.1" required="true">');
    $('.confidence-input').append($confidenceInput);
    $confidenceInput.val(defaultConfidence);

    let $stitchButton = $('<button class="btn btn-warning mb-3 mt-2 text-nowrap" type="button">Update Stitching</button>');
    if (json_context.disable_stitching) {
        $stitchButton.prop('disabled', true);
    }
    $('.stitch-button').append($stitchButton);
    $stitchButton.on('click', function () {
        const confidence = $confidenceInput[0].value;
        localStorage.setItem(confidenceStorageKey, confidence);
        const params = `?guid=${json_context.guid}&confidence_threshold=${confidence}`;
        $(this).prop('disabled', true);
        updateStitching(json_context.STITCHER_URL + '/update-stitching/' + params, {
            panoramaStatusUrl: json_context.panorama_status_url,
            initialTimestamp: json_context.panorama_timestamp,
            initialPath: json_context.panorama_path,
        });
    });

    let $useSampleId = $(`<button class="btn btn-warning btn-small text-nowrap" type="button">Use ${json_context.first_potential_sample}</button>`)
    $('.use-sample-id').append($useSampleId)
    $useSampleId.on('click', function() {
        $('#id_bugbox_sample_id').val(json_context.first_potential_sample);
    });

    let $notaSample = $(`<input class="form-check-input" type="checkbox" value="" id="notaSampleCheck">`)
    $('.nota-sample-check').append($notaSample)

    let $deleteButton = $(`<a href="${json_context.stitcher_delete_url}" class="btn btn-danger mb-3 mt-2 text-nowrap" type="button">Delete</a>`)
    if ( json_context.disable_delete ) {
        $deleteButton.addClass('disabled');
    }
    $('.delete-button').append($deleteButton)

})
