document.addEventListener('DOMContentLoaded', function() {
    try {
        initCropTypeConditionals();
        initCoverCropConditionals();
        initOrganicAmendmentConditionals();
        initTillageConditionals();
        initManagementPracticesConditionals();
    } catch (error) {
        console.warn('Conditional fields initialization error:', error);
    }
});

function initCropTypeConditionals() {
    const fieldTypeField = document.getElementById('id_field_type');
    const cropTypeField = document.getElementById('id_crop_type');
    const cropSubtypeField = document.getElementById('id_crop_subtype');
    const cropSubtypeOtherField = document.getElementById('id_crop_subtype_other');
    const smallGrainTypeField = document.getElementById('id_small_grain_type');
    const orchardCropTypeField = document.getElementById('id_orchard_crop_type');
    const orchardCropSpecifyField = document.getElementById('id_orchard_crop_specify');
    const orchardCropSpecifyContainer = document.getElementById('orchard_crop_specify_container');

    if (!fieldTypeField) return;

    function updateCropTypeFields() {
        const fieldType = fieldTypeField.value;
        
        const cropTypeFields = document.getElementById('crop_type_fields');
        if (fieldType === 'crop' && cropTypeFields) {
            cropTypeFields.style.display = 'block';
        } else if (cropTypeFields) {
            cropTypeFields.style.display = 'none';
        }
        
        const orchardCropTypeFields = document.getElementById('orchard_crop_type_fields');
        if (fieldType === 'orchard' && orchardCropTypeFields) {
            orchardCropTypeFields.style.display = 'block';
        } else if (orchardCropTypeFields) {
            orchardCropTypeFields.style.display = 'none';
        }

        const cropType = cropTypeField ? cropTypeField.value : '';
        const cropSubtypeContainer = document.getElementById('crop_subtype_container');
        
        if (cropType === 'row_crop') {
            if (cropSubtypeContainer) {
                cropSubtypeContainer.style.display = 'block';
            }
        } else {
            if (cropSubtypeContainer) {
                cropSubtypeContainer.style.display = 'none';
            }
            if (cropSubtypeField) {
                cropSubtypeField.value = '';
            }
        }
        
        const orchardCropType = orchardCropTypeField ? orchardCropTypeField.value : '';
        
        if (orchardCropType === 'fruit_trees' || orchardCropType === 'nut_trees') {
            if (orchardCropSpecifyContainer) {
                orchardCropSpecifyContainer.style.display = 'block';
            }
            if (orchardCropSpecifyField) {
                const label = orchardCropSpecifyField.closest('.form-group')?.querySelector('label');
                if (label) {
                    label.textContent = orchardCropType === 'fruit_trees' ? 'Specify fruit trees:' : 'Specify nut trees:';
                }
            }
        } else {
            if (orchardCropSpecifyContainer) {
                orchardCropSpecifyContainer.style.display = 'none';
            }
            if (orchardCropSpecifyField) {
                orchardCropSpecifyField.value = '';
            }
        }
        
        const tillageMethodsField = document.getElementById('id_tillage_methods');
        if (tillageMethodsField) {
            const tillageMethodsContainer = tillageMethodsField.closest('.form-group');
            if (tillageMethodsContainer) {
                if (fieldType === 'crop') {
                    tillageMethodsContainer.style.display = 'block';
                } else {
                    tillageMethodsContainer.style.display = 'none';
                }
            }
        }
    }

    function updateCropSubtypeFields() {
        const cropSubtype = cropSubtypeField ? cropSubtypeField.value : '';
        
        const cropSubtypeOtherContainer = document.getElementById('crop_subtype_other_container');
        if (cropSubtype === 'other') {
            if (cropSubtypeOtherContainer) {
                cropSubtypeOtherContainer.style.display = 'block';
            }
        } else {
            if (cropSubtypeOtherContainer) {
                cropSubtypeOtherContainer.style.display = 'none';
            }
            if (cropSubtypeOtherField) {
                cropSubtypeOtherField.value = '';
            }
        }

        const smallGrainContainer = document.getElementById('small_grain_container');
        if (cropSubtype === 'small_grain') {
            if (smallGrainContainer) {
                smallGrainContainer.style.display = 'block';
            }
        } else {
            if (smallGrainContainer) {
                smallGrainContainer.style.display = 'none';
            }
            if (smallGrainTypeField) {
                smallGrainTypeField.value = '';
            }
        }
    }

    fieldTypeField.addEventListener('change', updateCropTypeFields);
    if (cropTypeField) {
        cropTypeField.addEventListener('change', updateCropTypeFields);
    }
    if (cropSubtypeField) {
        cropSubtypeField.addEventListener('change', updateCropSubtypeFields);
    }
    if (orchardCropTypeField) {
        orchardCropTypeField.addEventListener('change', updateCropTypeFields);
    }

    updateCropTypeFields();
    updateCropSubtypeFields();
}

function initCoverCropConditionals() {
    const coverCropField = document.getElementById('id_uses_cover_crop');
    const terminationField = document.getElementById('id_cover_crop_termination');
    const terminationOtherField = document.getElementById('id_cover_crop_termination_other');
    const coverCropFields = document.getElementById('cover_crop_fields');

    if (!coverCropField || !coverCropFields) return;

    function updateCoverCropFields() {
        if (coverCropField.checked) {
            coverCropFields.style.display = 'block';
        } else {
            coverCropFields.style.display = 'none';
            if (terminationField) terminationField.value = '';
            if (terminationOtherField) terminationOtherField.value = '';
        }
    }

    function updateTerminationFields() {
        const termination = terminationField ? terminationField.value : '';
        const terminationOtherContainer = document.getElementById('cover_crop_termination_other_container');
        
        if (termination === 'other') {
            if (terminationOtherContainer) {
                terminationOtherContainer.style.display = 'block';
            }
        } else {
            if (terminationOtherContainer) {
                terminationOtherContainer.style.display = 'none';
            }
            if (terminationOtherField) {
                terminationOtherField.value = '';
            }
        }
    }

    coverCropField.addEventListener('change', updateCoverCropFields);
    if (terminationField) {
        terminationField.addEventListener('change', updateTerminationFields);
    }

    updateCoverCropFields();
    updateTerminationFields();
}

function initOrganicAmendmentConditionals() {
    const organicAmendmentField = document.getElementById('id_uses_organic_amendments');
    const amendmentTypesField = document.getElementById('id_organic_amendment_types');
    const amendmentOtherField = document.getElementById('id_organic_amendment_other');
    const organicAmendmentFields = document.getElementById('organic_amendment_fields');

    if (!organicAmendmentField || !organicAmendmentFields) return;

    function updateOrganicAmendmentFields() {
        if (organicAmendmentField.checked) {
            organicAmendmentFields.style.display = 'block';
        } else {
            organicAmendmentFields.style.display = 'none';
            if (amendmentTypesField) amendmentTypesField.value = '';
            if (amendmentOtherField) amendmentOtherField.value = '';
        }
    }

    function updateAmendmentTypeFields() {
        const amendmentType = amendmentTypesField ? amendmentTypesField.value : '';
        const amendmentOtherContainer = document.getElementById('organic_amendment_other_container');
        
        if (amendmentType === 'other') {
            if (amendmentOtherContainer) {
                amendmentOtherContainer.style.display = 'block';
            }
        } else {
            if (amendmentOtherContainer) {
                amendmentOtherContainer.style.display = 'none';
            }
            if (amendmentOtherField) {
                amendmentOtherField.value = '';
            }
        }
    }

    organicAmendmentField.addEventListener('change', updateOrganicAmendmentFields);
    if (amendmentTypesField) {
        amendmentTypesField.addEventListener('change', updateAmendmentTypeFields);
    }

    updateOrganicAmendmentFields();
    updateAmendmentTypeFields();
}

function initTillageConditionals() {
    const tillageField = document.getElementById('id_uses_tillage');
    const tillageDepthField = document.getElementById('id_tillage_depth');
    const tillageDepthContainer = document.getElementById('tillage_depth_field');

    if (!tillageField || !tillageDepthContainer) return;

    function updateTillageFields() {
        if (tillageField.checked) {
            tillageDepthContainer.style.display = 'block';
        } else {
            tillageDepthContainer.style.display = 'none';
            if (tillageDepthField) tillageDepthField.value = '';
        }
    }

    tillageField.addEventListener('change', updateTillageFields);

    updateTillageFields();
}

function initManagementPracticesConditionals() {
    const grazerTypesField = document.getElementById('id_grazer_types');
    if (grazerTypesField) {
        grazerTypesField.addEventListener('change', updateGrazerTypesFields);
    }

    const groundCoverField = document.getElementById('id_ground_cover_management');
    if (groundCoverField) {
        groundCoverField.addEventListener('change', updateGroundCoverManagementFields);
    }

    const tillsBetweenRows = document.getElementById('id_tills_between_rows');
    if (tillsBetweenRows) {
        tillsBetweenRows.addEventListener('change', updateOrchardTillageDepth);
    }
    
    const fieldTypeField = document.getElementById('id_field_type');
    if (fieldTypeField) {
        fieldTypeField.addEventListener('change', updateFieldTypeSpecificSections);
        fieldTypeField.addEventListener('change', updateRangelandSpecificSections);
    }

    updateGrazerTypesFields();
    updateGroundCoverManagementFields();
    updateOrchardTillageDepth();
    updateFieldTypeSpecificSections();
    updateRangelandSpecificSections();

    const grazedCurrentYearField = document.getElementById('id_grazed_current_year');
    const notGrazedCommentsContainer = document.getElementById('not_grazed_comments_container');
    function updateGrazedComments() {
        if (!grazedCurrentYearField || !notGrazedCommentsContainer) return;
        if (grazedCurrentYearField.checked) {
            notGrazedCommentsContainer.style.display = 'none';
        } else {
            notGrazedCommentsContainer.style.display = 'block';
        }
    }
    if (grazedCurrentYearField) {
        grazedCurrentYearField.addEventListener('change', updateGrazedComments);
        updateGrazedComments();
    }

    const appliesInsectDewormersField = document.getElementById('id_applies_insecticides_dewormers');
    const insectDewormerFields = document.getElementById('insecticide_dewormer_fields');
    function updateInsectDewormer() {
        if (!appliesInsectDewormersField || !insectDewormerFields) return;
        if (appliesInsectDewormersField.checked) {
            insectDewormerFields.style.display = 'block';
        } else {
            insectDewormerFields.style.display = 'none';
        }
    }
    if (appliesInsectDewormersField) {
        appliesInsectDewormersField.addEventListener('change', updateInsectDewormer);
        updateInsectDewormer();
    }

    setTimeout(() => {
        updateFieldTypeSpecificSections();
        updateRangelandSpecificSections();
    }, 500);
}

function updateGrazerTypesFields() {
    const grazerTypesField = document.getElementById('id_grazer_types');
    const grazerTypesOtherContainer = document.getElementById('grazer_types_other_container');
    
    if (grazerTypesField && grazerTypesOtherContainer) {
        if (grazerTypesField.value === 'other') {
            grazerTypesOtherContainer.style.display = 'block';
        } else {
            grazerTypesOtherContainer.style.display = 'none';
        }
    }
}

function updateGroundCoverManagementFields() {
    const groundCoverField = document.getElementById('id_ground_cover_management');
    const groundCoverOtherContainer = document.getElementById('ground_cover_management_other_container');
    
    if (groundCoverField && groundCoverOtherContainer) {
        if (groundCoverField.value === 'other') {
            groundCoverOtherContainer.style.display = 'block';
        } else {
            groundCoverOtherContainer.style.display = 'none';
        }
    }
}

function updateOrchardTillageDepth() {
    const tillsBetweenRows = document.getElementById('id_tills_between_rows');
    const fieldTypeField = document.getElementById('id_field_type');
    const depthContainer = document.getElementById('tillage_depth_field');
    const orchardMount = document.getElementById('orchard_tillage_depth_mount');
    if (!tillsBetweenRows || !depthContainer || !orchardMount || !fieldTypeField) return;
    const isOrchard = fieldTypeField.value === 'orchard';
    if (isOrchard) {
        if (!orchardMount.contains(depthContainer)) {
            orchardMount.appendChild(depthContainer);
        }
        orchardMount.style.display = tillsBetweenRows.checked ? 'block' : 'none';
    } else {
        orchardMount.style.display = 'none';
    }
}

function getFieldType() {
    const jsonContext = document.getElementById('json_context');
    let fieldType = null;
    
    if (jsonContext) {
        try {
            const context = JSON.parse(jsonContext.textContent);
            fieldType = context.fieldType;
        } catch (e) {
            console.warn('Could not parse JSON context:', e);
        }
    }
    
    if (!fieldType) {
        const fieldTypeField = document.getElementById('id_field_type');
        fieldType = fieldTypeField ? fieldTypeField.value : null;
    }
    
    return fieldType;
}

function updateFieldTypeSpecificSections() {
    const fieldType = getFieldType();
    if (!fieldType) return;
    
    const tillageSection = document.getElementById('tillage_practices_section');
    const tillageByClass = document.querySelector('.non-orchard-only');
    const dairyFields = document.getElementById('dairy_fields');
    
    function hideSection(section) {
        if (section) {
            section.style.setProperty('display', 'none', 'important');
            if (fieldType === 'orchard') {
                section.classList.add('hidden-for-orchard');
                section.style.visibility = 'hidden';
                section.style.height = '0';
                section.style.overflow = 'hidden';
            } else if (fieldType === 'range') {
                section.classList.add('hidden-for-rangeland');
            }
        }
    }
    
    function showSection(section) {
        if (section) {
            section.style.setProperty('display', 'block', 'important');
            section.classList.remove('hidden-for-orchard', 'hidden-for-rangeland');
        }
    }
    
    if (fieldType === 'orchard' || fieldType === 'range') {
        hideSection(tillageSection);
        hideSection(tillageByClass);
        hideSection(dairyFields);
    } else {
        showSection(tillageSection);
        showSection(tillageByClass);
        showSection(dairyFields);
    }
}

function updateRangelandSpecificSections() {
    const fieldType = getFieldType();
    if (!fieldType) return;
    
    document.querySelectorAll('.non-rangeland-only').forEach(section => {
        section.style.display = 'block';
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                const tillageSection = document.getElementById('tillage_practices_section');
                if (tillageSection && tillageSection.style.display !== 'none') {
                    updateFieldTypeSpecificSections();
                }
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

