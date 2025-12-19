document.addEventListener('DOMContentLoaded', function() {
    const labelCategory = document.getElementById('id_label_category');
    const projectType = document.getElementById('id_project_type');
    const innerSection = document.getElementById('inner-labels-section');
    const outerMessage = document.getElementById('outer-labels-message');
    const avalancheSampleTypes = document.getElementById('avalanche-sample-types');
    const thousandFarmsSampleTypes = document.getElementById('1000farms-sample-types');
    
    function toggleSections() {
        if (labelCategory && labelCategory.value === 'inner') {
            if (innerSection) innerSection.style.display = 'block';
            if (outerMessage) outerMessage.style.display = 'none';
            toggleSampleTypes();
        } else if (labelCategory && labelCategory.value === 'outer') {
            if (innerSection) innerSection.style.display = 'none';
            if (outerMessage) outerMessage.style.display = 'block';
        } else {
            if (innerSection) innerSection.style.display = 'none';
            if (outerMessage) outerMessage.style.display = 'none';
        }
    }
    
    function toggleSampleTypes() {
        document.querySelectorAll('.sample-type-checkbox').forEach(function(checkbox) {
            checkbox.checked = false;
        });
        
        if (projectType && projectType.value === 'avalanche') {
            if (avalancheSampleTypes) avalancheSampleTypes.style.display = 'block';
            if (thousandFarmsSampleTypes) thousandFarmsSampleTypes.style.display = 'none';
        } else if (projectType && projectType.value === '1000_farms') {
            if (avalancheSampleTypes) avalancheSampleTypes.style.display = 'none';
            if (thousandFarmsSampleTypes) thousandFarmsSampleTypes.style.display = 'block';
        }
    }
    
    if (labelCategory) {
        labelCategory.addEventListener('change', toggleSections);
    }
    
    if (projectType) {
        projectType.addEventListener('change', toggleSampleTypes);
    }
    
    toggleSections();
});

