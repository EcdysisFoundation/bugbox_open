document.addEventListener('DOMContentLoaded', function() {
    const fieldTypeSelect = document.getElementById('id_field_type');
    const cropVarietyField = document.getElementById('crop_variety_field');
    const rangelandFields = document.getElementById('rangeland_fields');
    const orchardSpecificFields = document.getElementById('orchard_specific_fields');
    
    function updateFieldDisplay() {
        const fieldType = fieldTypeSelect.value;
        
        if (cropVarietyField) cropVarietyField.style.display = 'none';
        if (rangelandFields) rangelandFields.style.display = 'none';
        if (orchardSpecificFields) orchardSpecificFields.style.display = 'none';
        
        if (fieldType === 'crop') {
            if (cropVarietyField) cropVarietyField.style.display = 'block';
        } else if (fieldType === 'range') {
            if (rangelandFields) rangelandFields.style.display = 'block';
        } else if (fieldType === 'orchard') {
            if (cropVarietyField) cropVarietyField.style.display = 'block';
            if (orchardSpecificFields) orchardSpecificFields.style.display = 'block';
        }
    }
    
    if (fieldTypeSelect) {
        fieldTypeSelect.addEventListener('change', updateFieldDisplay);
        updateFieldDisplay();
    }
});

