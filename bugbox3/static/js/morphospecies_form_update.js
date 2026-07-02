import $ from 'jquery';

function clearSection($section) {
    $section.find('.fg-trait-checkbox').prop('checked', false);
}

function initParentSubtypeSection($section) {
    $section.on('click', '.fg-clear-section', function onClear() {
        clearSection($section);
    });

    $section.on('change', '.fg-subtype-checkbox', function onSubtypeChange() {
        if (!$(this).is(':checked')) {
            return;
        }
        const parentCode = $section.attr('data-parent-code');
        $section.find(`[data-fg-code="${parentCode}"] .fg-parent-checkbox`).prop('checked', true);
    });
}

$(function initFunctionalGroupCheckboxes() {
    $('.fg-section-parent').each(function initSection() {
        initParentSubtypeSection($(this));
    });
});
