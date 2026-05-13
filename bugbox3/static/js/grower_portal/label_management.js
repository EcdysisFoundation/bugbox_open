document.addEventListener('DOMContentLoaded', function() {
    const labelCategorySelect = document.getElementById('id_quick_label_category');
    const numberOfTransectsSection = document.getElementById('inner-labels-quick-section');
    const outerLabelsSection = document.getElementById('outer-labels-quick-section');
    const innerLabelGenerationSelect = document.getElementById('id_inner_label_generation');
    const clusterNumberInput = document.getElementById('id_quick_cluster_number');
    const yearInput = document.getElementById('id_quick_year');
    const projectTypeSelect = document.getElementById('id_quick_project_type');
    const quickLabelForm = document.getElementById('quick-label-form');
    const igniteInnerForageRow = document.getElementById('ignite-inner-forage-row');
    const includeForageInput = document.getElementById('id_include_forage_labels');
    
    // Get the inner label generations URL from the form's data attribute
    const innerLabelGenerationsUrl = quickLabelForm ? quickLabelForm.getAttribute('data-inner-label-generations-url') : null;
    
    function updateIgniteForageRowVisibility() {
        const labelCategory = labelCategorySelect ? labelCategorySelect.value : 'inner';
        const projectType = projectTypeSelect ? projectTypeSelect.value : '';
        const show = projectType === 'ignite' && labelCategory === 'inner';
        if (igniteInnerForageRow) {
            igniteInnerForageRow.style.display = show ? 'block' : 'none';
        }
        if (includeForageInput) {
            includeForageInput.disabled = !show;
            if (!show) {
                includeForageInput.checked = false;
            }
        }
    }
    
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
        updateIgniteForageRowVisibility();
    }
    
    function loadInnerLabelGenerations() {
        if (!innerLabelGenerationSelect || !clusterNumberInput || !yearInput || !projectTypeSelect || !innerLabelGenerationsUrl) {
            return;
        }
        
        const clusterNumber = clusterNumberInput.value.trim();
        const year = yearInput.value.trim();
        const projectType = projectTypeSelect.value.trim();
        
        if (!clusterNumber || !year || !projectType) {
            innerLabelGenerationSelect.innerHTML = '<option value="">-- Enter cluster, year, and project type first --</option>';
            return;
        }
        
        const url = innerLabelGenerationsUrl + '?cluster=' + encodeURIComponent(clusterNumber) + '&year=' + encodeURIComponent(year) + '&project_type=' + encodeURIComponent(projectType);
        fetch(url)
            .then(response => response.json())
            .then(data => {
                innerLabelGenerationSelect.innerHTML = '<option value="">-- Select inner label generation --</option>';
                
                if (data.generations && data.generations.length > 0) {
                    data.generations.forEach(gen => {
                        const option = document.createElement('option');
                        option.value = gen.id;
                        const projectLabel = gen.project_type_display ? '[' + gen.project_type_display + '] ' : '';
                        option.textContent = projectLabel + 'Generated on ' + gen.generated_at + ' - ' + gen.total_labels + ' labels - ' + gen.transect_count + ' sites/transects';
                        innerLabelGenerationSelect.appendChild(option);
                    });
                } else {
                    const option = document.createElement('option');
                    option.value = '';
                    option.textContent = 'No inner label generations found for this project/cluster/year';
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
    
    if (clusterNumberInput && yearInput && projectTypeSelect) {
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
        projectTypeSelect.addEventListener('change', function() {
            updateIgniteForageRowVisibility();
            if (labelCategorySelect && labelCategorySelect.value === 'outer') {
                loadInnerLabelGenerations();
            }
        });
    }
});
