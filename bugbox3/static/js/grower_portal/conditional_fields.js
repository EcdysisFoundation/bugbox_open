/**
 * Conditional Fields JavaScript for Grower Portal Forms
 * Handles show/hide logic for conditional form fields
 */

document.addEventListener('DOMContentLoaded', function() {
    try {
        initCropTypeConditionals();
        initCoverCropConditionals();
        initOrganicAmendmentConditionals();
        initTillageConditionals();
        initCoverCropUsageConditionals();
        initOrganicAmendmentUsageConditionals();
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
    const broadForkField = document.getElementById('id_uses_broad_fork');
    const broadForkContainer = broadForkField ? broadForkField.closest('.form-group') : null;
    
    const orchardCropTypeField = document.getElementById('id_orchard_crop_type');
    const orchardCropSubtypeField = document.getElementById('id_orchard_crop_subtype');
    const orchardCropSubtypeOtherField = document.getElementById('id_orchard_crop_subtype_other');
    const orchardSmallGrainTypeField = document.getElementById('id_orchard_small_grain_type');
    const orchardBroadForkField = document.getElementById('id_orchard_uses_broad_fork');

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
        const orchardCropSubtypeContainer = document.getElementById('orchard_crop_subtype_container');
        
        if (orchardCropType === 'row_crop') {
            if (orchardCropSubtypeContainer) {
                orchardCropSubtypeContainer.style.display = 'block';
            }
        } else {
            if (orchardCropSubtypeContainer) {
                orchardCropSubtypeContainer.style.display = 'none';
            }
            if (orchardCropSubtypeField) {
                orchardCropSubtypeField.value = '';
            }
        }

        const broadForkContainer = document.getElementById('broad_fork_container');
        if (cropType === 'mixed_veg') {
            if (broadForkContainer) {
                broadForkContainer.style.display = 'block';
            }
        } else {
            if (broadForkContainer) {
                broadForkContainer.style.display = 'none';
            }
            if (broadForkField) broadForkField.checked = false;
        }
        
        const orchardBroadForkContainer = document.getElementById('orchard_broad_fork_container');
        if (orchardCropType === 'mixed_veg') {
            if (orchardBroadForkContainer) {
                orchardBroadForkContainer.style.display = 'block';
            }
        } else {
            if (orchardBroadForkContainer) {
                orchardBroadForkContainer.style.display = 'none';
            }
            if (orchardBroadForkField) orchardBroadForkField.checked = false;
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
    
    function updateOrchardCropSubtypeFields() {
        const orchardCropSubtype = orchardCropSubtypeField ? orchardCropSubtypeField.value : '';
        
        const orchardCropSubtypeOtherContainer = document.getElementById('orchard_crop_subtype_other_container');
        if (orchardCropSubtype === 'other') {
            if (orchardCropSubtypeOtherContainer) {
                orchardCropSubtypeOtherContainer.style.display = 'block';
            }
        } else {
            if (orchardCropSubtypeOtherContainer) {
                orchardCropSubtypeOtherContainer.style.display = 'none';
            }
            if (orchardCropSubtypeOtherField) {
                orchardCropSubtypeOtherField.value = '';
            }
        }

        const orchardSmallGrainContainer = document.getElementById('orchard_small_grain_container');
        if (orchardCropSubtype === 'small_grain') {
            if (orchardSmallGrainContainer) {
                orchardSmallGrainContainer.style.display = 'block';
            }
        } else {
            if (orchardSmallGrainContainer) {
                orchardSmallGrainContainer.style.display = 'none';
            }
            if (orchardSmallGrainTypeField) {
                orchardSmallGrainTypeField.value = '';
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
    if (orchardCropSubtypeField) {
        orchardCropSubtypeField.addEventListener('change', updateOrchardCropSubtypeFields);
    }

    updateCropTypeFields();
    updateCropSubtypeFields();
    updateOrchardCropSubtypeFields();
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

function initCoverCropUsageConditionals() {
    const coverCropField = document.getElementById('id_uses_cover_crop');
    const terminationField = document.getElementById('id_cover_crop_termination');
    const terminationOtherField = document.getElementById('id_cover_crop_termination_other');
    const coverCropFields = document.getElementById('cover_crop_fields');

    if (!coverCropField || !coverCropFields) return;

    function updateCoverCropUsageFields() {
        if (coverCropField.checked) {
            coverCropFields.style.display = 'block';
        } else {
            coverCropFields.style.display = 'none';
            if (terminationField) terminationField.value = '';
            if (terminationOtherField) terminationOtherField.value = '';
        }
    }

    function updateTerminationUsageFields() {
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

    coverCropField.addEventListener('change', updateCoverCropUsageFields);
    if (terminationField) {
        terminationField.addEventListener('change', updateTerminationUsageFields);
    }

    updateCoverCropUsageFields();
    updateTerminationUsageFields();
}

function initOrganicAmendmentUsageConditionals() {
    const organicAmendmentField = document.getElementById('id_uses_organic_amendments');
    const amendmentTypesField = document.getElementById('id_organic_amendment_types');
    const amendmentOtherField = document.getElementById('id_organic_amendment_other');
    const organicAmendmentFields = document.getElementById('organic_amendment_fields');

    if (!organicAmendmentField || !organicAmendmentFields) return;

    function updateOrganicAmendmentUsageFields() {
        if (organicAmendmentField.checked) {
            organicAmendmentFields.style.display = 'block';
        } else {
            organicAmendmentFields.style.display = 'none';
            if (amendmentTypesField) amendmentTypesField.value = '';
            if (amendmentOtherField) amendmentOtherField.value = '';
        }
    }

    function updateAmendmentTypeUsageFields() {
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

    organicAmendmentField.addEventListener('change', updateOrganicAmendmentUsageFields);
    if (amendmentTypesField) {
        amendmentTypesField.addEventListener('change', updateAmendmentTypeUsageFields);
    }
    
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

    updateOrganicAmendmentUsageFields();
    updateAmendmentTypeUsageFields();
    
    updateGrazerTypesFields();
    updateGroundCoverManagementFields();
    updateOrchardTillageDepth();
    updateFieldTypeSpecificSections();
    updateRangelandSpecificSections();
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
    const orchardTillageDepthField = document.getElementById('orchard_tillage_depth_field');
    
    if (tillsBetweenRows && orchardTillageDepthField) {
        if (tillsBetweenRows.checked) {
            orchardTillageDepthField.style.display = 'block';
        } else {
            orchardTillageDepthField.style.display = 'none';
        }
    }
}

function updateFieldTypeSpecificSections() {
    const fieldTypeField = document.getElementById('id_field_type');
    if (!fieldTypeField) return;
    
    const fieldType = fieldTypeField.value;
    const tillageSection = document.getElementById('tillage_practices_section');
    const dairyFields = document.getElementById('dairy_fields');
    
    if (fieldType === 'orchard') {
        if (tillageSection) tillageSection.style.display = 'none';
        if (dairyFields) dairyFields.style.display = 'none';
    } else {
        if (tillageSection) tillageSection.style.display = 'block';
        if (dairyFields) dairyFields.style.display = 'block';
    }
}

function updateRangelandSpecificSections() {
    const fieldTypeField = document.getElementById('id_field_type');
    if (!fieldTypeField) return;
    
    const fieldType = fieldTypeField.value;
    
    if (fieldType === 'range') {
        document.querySelectorAll('.non-rangeland-only').forEach(section => {
            section.style.display = 'none';
        });
    } else {
        document.querySelectorAll('.non-rangeland-only').forEach(section => {
            section.style.display = 'block';
        });
    }
}
