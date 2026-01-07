document.addEventListener('DOMContentLoaded', function() {
    const labelCategorySelect = document.getElementById('id_quick_label_category');
    const numberOfTransectsSection = document.getElementById('inner-labels-quick-section');
    const outerLabelsSection = document.getElementById('outer-labels-quick-section');
    const innerLabelGenerationSelect = document.getElementById('id_inner_label_generation');
    const clusterNumberInput = document.getElementById('id_quick_cluster_number');
    const yearInput = document.getElementById('id_quick_year');
    const quickLabelForm = document.getElementById('quick-label-form');
    
    // Get the inner label generations URL from the form's data attribute
    const innerLabelGenerationsUrl = quickLabelForm ? quickLabelForm.getAttribute('data-inner-label-generations-url') : null;
    
    function updateFormVisibility() {
        const labelCategory = labelCategorySelect ? labelCategorySelect.value : 'inner';
        
        if (labelCategory === 'outer') {
            if (numberOfTransectsSection) numberOfTransectsSection.style.display = 'none';
            if (outerLabelsSection) outerLabelsSection.style.display = 'flex';
            loadInnerLabelGenerations();
        } else {
            if (numberOfTransectsSection) numberOfTransectsSection.style.display = 'flex';
            if (outerLabelsSection) outerLabelsSection.style.display = 'none';
        }
    }
    
    function loadInnerLabelGenerations() {
        if (!innerLabelGenerationSelect || !clusterNumberInput || !yearInput || !innerLabelGenerationsUrl) {
            return;
        }
        
        const clusterNumber = clusterNumberInput.value.trim();
        const year = yearInput.value.trim();
        
        if (!clusterNumber || !year) {
            innerLabelGenerationSelect.innerHTML = '<option value="">-- Enter cluster and year first --</option>';
            return;
        }
        
        const url = innerLabelGenerationsUrl + '?cluster=' + encodeURIComponent(clusterNumber) + '&year=' + encodeURIComponent(year);
        fetch(url)
            .then(response => response.json())
            .then(data => {
                innerLabelGenerationSelect.innerHTML = '<option value="">-- Select inner label generation --</option>';
                
                if (data.generations && data.generations.length > 0) {
                    data.generations.forEach(gen => {
                        const option = document.createElement('option');
                        option.value = gen.id;
                        option.textContent = 'Generated on ' + gen.generated_at + ' - ' + gen.total_labels + ' labels - ' + gen.transect_count + ' transects';
                        innerLabelGenerationSelect.appendChild(option);
                    });
                } else {
                    const option = document.createElement('option');
                    option.value = '';
                    option.textContent = 'No inner label generations found for this cluster/year';
                    innerLabelGenerationSelect.appendChild(option);
                }
            })
            .catch(error => {
                console.error('Error loading inner label generations:', error);
                innerLabelGenerationSelect.innerHTML = '<option value="">Error loading generations</option>';
            });
    }
    
    if (labelCategorySelect) {
        labelCategorySelect.addEventListener('change', updateFormVisibility);
        updateFormVisibility();
    }
    
    if (clusterNumberInput && yearInput) {
        clusterNumberInput.addEventListener('blur', function() {
            if (labelCategorySelect && labelCategorySelect.value === 'outer') {
                loadInnerLabelGenerations();
            }
        });
        yearInput.addEventListener('blur', function() {
            if (labelCategorySelect && labelCategorySelect.value === 'outer') {
                loadInnerLabelGenerations();
            }
        });
    }
});
