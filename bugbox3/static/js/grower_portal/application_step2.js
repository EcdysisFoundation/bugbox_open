document.addEventListener('DOMContentLoaded', function() {
    const usesTillage = document.getElementById('id_uses_tillage');
    const tillageDepthField = document.getElementById('tillage_depth_field');
    
    const usesCoverCrop = document.getElementById('id_uses_cover_crop');
    const coverCropFields = document.getElementById('cover_crop_fields');
    
    const usesOrganicAmendments = document.getElementById('id_uses_organic_amendments');
    const organicAmendmentFields = document.getElementById('organic_amendment_fields');
    
    const usesGrazing = document.getElementById('id_uses_grazing');
    const grazingFields = document.getElementById('grazing_fields');
    
    const appliesInsecticides = document.getElementById('id_applies_insecticides_dewormers');
    const insecticideFields = document.getElementById('insecticide_fields');
    
    const allowsGroundCover = document.getElementById('id_allows_ground_cover');
    const groundCoverFields = document.getElementById('ground_cover_fields');
    
    function toggleField(checkbox, targetDiv) {
        if (checkbox && targetDiv) {
            targetDiv.style.display = checkbox.checked ? 'block' : 'none';
        }
    }
    
    if (usesTillage) usesTillage.addEventListener('change', () => toggleField(usesTillage, tillageDepthField));
    if (usesCoverCrop) usesCoverCrop.addEventListener('change', () => toggleField(usesCoverCrop, coverCropFields));
    if (usesOrganicAmendments) usesOrganicAmendments.addEventListener('change', () => toggleField(usesOrganicAmendments, organicAmendmentFields));
    if (usesGrazing) usesGrazing.addEventListener('change', () => toggleField(usesGrazing, grazingFields));
    if (appliesInsecticides) appliesInsecticides.addEventListener('change', () => toggleField(appliesInsecticides, insecticideFields));
    if (allowsGroundCover) allowsGroundCover.addEventListener('change', () => toggleField(allowsGroundCover, groundCoverFields));
    
    toggleField(usesTillage, tillageDepthField);
    toggleField(usesCoverCrop, coverCropFields);
    toggleField(usesOrganicAmendments, organicAmendmentFields);
    toggleField(usesGrazing, grazingFields);
    toggleField(appliesInsecticides, insecticideFields);
    toggleField(allowsGroundCover, groundCoverFields);
    
    const jsonContext = JSON.parse(document.getElementById('json_context').textContent);
    const orchardPractices = document.getElementById('orchard_practices');
    
    if (orchardPractices && jsonContext.fieldType) {
        orchardPractices.style.display = (jsonContext.fieldType === 'orchard') ? 'block' : 'none';
    }
});

