document.addEventListener('DOMContentLoaded', function() {
    const addButton = document.getElementById('add-grazing-event-btn');
    const eventCountSpan = document.getElementById('event-count');
    const allForms = document.querySelectorAll('.grazing-event-form');
    const maxEvents = 4;
    
    function updateEventCount() {
        const visibleForms = document.querySelectorAll('.grazing-event-form:not([style*="display:none"]):not([style*="display: none"])');
        const count = visibleForms.length;
        eventCountSpan.textContent = count;
        
        if (count >= maxEvents) {
            addButton.style.display = 'none';
        } else {
            addButton.style.display = 'inline-block';
        }
        
        document.querySelectorAll('.remove-event-btn').forEach(btn => btn.style.display = 'none');
        
        if (visibleForms.length > 1) {
            const lastVisibleForm = visibleForms[visibleForms.length - 1];
            const lastFormIndex = lastVisibleForm.getAttribute('data-form-index');
            
            if (lastFormIndex !== '0') {
                const removeBtn = lastVisibleForm.querySelector('.remove-event-btn');
                if (removeBtn) {
                    removeBtn.style.display = 'inline-block';
                }
            }
        }
    }
    
    if (addButton) {
        addButton.addEventListener('click', function() {
            const hiddenForms = document.querySelectorAll('.grazing-event-form[style*="display:none"], .grazing-event-form[style*="display: none"]');
            
            if (hiddenForms.length > 0) {
                hiddenForms[0].style.display = 'block';
                updateEventCount();
            }
        });
    }
    
    document.querySelectorAll('.remove-event-btn').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const formIndex = this.getAttribute('data-form-index');
            const formCard = document.querySelector(`.grazing-event-form[data-form-index="${formIndex}"]`);
            const deleteCheckbox = formCard.querySelector('input[name$="-DELETE"]');
            
            if (deleteCheckbox) {
                deleteCheckbox.checked = true;
                formCard.style.display = 'none';
                updateEventCount();
            }
        });
    });
    
    updateEventCount();
});

