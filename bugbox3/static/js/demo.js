import $ from 'jquery';
import demoTour from './demo_tour';

function hideModal(modalId) {
    const modalElement = document.getElementById(modalId);
    if (!modalElement) return;
    
    if (typeof $ !== 'undefined' && $.fn.modal) {
        $(modalElement).modal('hide');
    } else if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) {
            modalInstance.hide();
        } else {
            const modal = new bootstrap.Modal(modalElement);
            modal.hide();
        }
    } else {
        const closeBtn = modalElement.querySelector('[data-bs-dismiss="modal"]');
        if (closeBtn) {
            closeBtn.click();
        } else {
            modalElement.classList.remove('show');
            modalElement.style.display = 'none';
            document.body.classList.remove('modal-open');
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) backdrop.remove();
        }
    }
}

function showDemoAlert(message, type = 'success') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = message;
    alert.style.position = 'fixed';
    alert.style.top = '20px';
    alert.style.right = '20px';
    alert.style.zIndex = '9999';
    document.body.appendChild(alert);
    setTimeout(() => alert.remove(), 3000);
}

function demoSubmitDetermination() {
    const selectedValue = document.querySelector('input[name="determin_picker"]:checked');
    if (!selectedValue) {
        alert('Please select an option');
        return;
    }
    
    const value = selectedValue.value;
    const btn = document.getElementById('aiPredictionBtn');
    if (!btn) return;
    
    btn.className = 'btn btn-sm ms-3';
    let text = '';
    if (value == '0') {
        btn.classList.add('btn-info');
        text = 'Pending';
    } else if (value == '1') {
        btn.classList.add('btn-success');
        text = 'Confirmed';
    } else if (value == '2') {
        btn.classList.add('btn-warning');
        text = 'Rejected';
    }
    btn.textContent = text;
    
    hideModal('confirmRejectModal');
    showDemoAlert('<i class="bi bi-check-circle"></i> Acceptance updated to "' + text + '" (Demo mode - not saved to database)', 'success');
}

function demoSetPrimaryImage() {
    const selected = document.querySelector('input[name="primary_picker"]:checked');
    if (!selected) {
        alert('Please select an image');
        return;
    }
    
    hideModal('setPrimaryModal');
    showDemoAlert('<i class="bi bi-check-circle"></i> Primary image set (Demo mode - not saved to database)', 'success');
}

function demoDeleteImage() {
    const selected = document.querySelector('input[name="delete_picker"]:checked');
    if (!selected) {
        alert('Please select an image');
        return;
    }
    
    hideModal('deleteModal');
    showDemoAlert('<i class="bi bi-check-circle"></i> Image deleted (Demo mode - not saved to database)', 'success');
}

function demoUploadImages(event) {
    event.preventDefault();
    const files = document.getElementById('image_files').files;
    if (files.length > 0) {
        showDemoAlert('<i class="bi bi-check-circle"></i> ' + files.length + ' image(s) uploaded (Demo mode - not saved to database)', 'success');
        document.getElementById('image_files').value = '';
    }
}

function demoEditSpecimen() {
    showDemoAlert('<i class="bi bi-info-circle"></i> Edit specimen functionality is not available in demo mode.', 'info');
}

function demoDeleteSpecimen() {
    if (confirm('This is a demo. The specimen will not actually be deleted. Continue?')) {
        showDemoAlert('<i class="bi bi-info-circle"></i> Delete specimen functionality is not available in demo mode.', 'info');
    }
}

window.demoSubmitDetermination = demoSubmitDetermination;
window.demoSetPrimaryImage = demoSetPrimaryImage;
window.demoDeleteImage = demoDeleteImage;
window.demoUploadImages = demoUploadImages;
window.demoEditSpecimen = demoEditSpecimen;
window.demoDeleteSpecimen = demoDeleteSpecimen;

$(function () {
    if ($('#experiments-table').length && window.location.pathname.includes('/demo/experiments')) {
        const tourButton = $('#start-tour-btn');
        if (tourButton.length) {
            tourButton.off('click');
            tourButton.on('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                e.stopImmediatePropagation();
                
                sessionStorage.removeItem('bugbox_demo_tour_active');
                sessionStorage.removeItem('bugbox_demo_tour_step');
                
                const $btn = $(this);
                $btn.prop('disabled', true);
                
                setTimeout(() => {
                    demoTour.start(0);
                    
                    setTimeout(() => {
                        $btn.prop('disabled', false);
                    }, 2000);
                }, 100);
            });
        } else {
            setTimeout(function() {
                const newButton = $('<button>', {
                    id: 'start-tour-btn',
                    class: 'btn btn-primary btn-lg',
                    html: '<i class="bi bi-compass"></i> Take a Guided Tour',
                    style: 'display: inline-flex; align-items: center; gap: 0.5rem;'
                });
                
                newButton.on('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    demoTour.start(0);
                });
                
                const header = $('.align-items-center.bg-ecdysis');
                if (header.length) {
                    header.append(newButton);
                }
            }, 500);
        }
    }

    demoTour.init();

    $('#submit-primary-btn').on('click', function(e) {
        e.preventDefault();
        demoSetPrimaryImage();
    });

    $('#delete-image-btn').on('click', function(e) {
        e.preventDefault();
        demoDeleteImage();
    });

    $('#submit-determination-btn').on('click', function(e) {
        e.preventDefault();
        demoSubmitDetermination();
    });

    $('#edit-specimen-btn').on('click', function(e) {
        e.preventDefault();
        demoEditSpecimen();
    });

    $('#delete-specimen-btn').on('click', function(e) {
        e.preventDefault();
        demoDeleteSpecimen();
    });

    $('#upload-images-form').on('submit', function(e) {
        demoUploadImages(e);
    });
});
