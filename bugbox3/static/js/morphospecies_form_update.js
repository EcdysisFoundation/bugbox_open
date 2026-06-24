import $ from 'jquery';

const TOLERANCE = 0.01;

function isOne(value) {
    const num = parseFloat(value);
    return !Number.isNaN(num) && Math.abs(num - 1) <= TOLERANCE;
}

function parseWeight(value) {
    const num = parseFloat(value);
    return Number.isNaN(num) ? 0 : num;
}

function setInputValue($input, value) {
    if (value === '' || value === null || value === undefined) {
        $input.val('');
    } else {
        $input.val(Number(value).toFixed(3).replace(/\.?0+$/, '') || '0');
    }
    $input.trigger('input');
}

function clearSection($section) {
    $section.find('.fg-weight-input').val('');
    $section.find('.fg-single-subtype-picker').val('');
    $section.find('.fg-other-toggle').prop('checked', false);
    updateParentSubtypeSection($section);
}

function applySingleSubtype($section, subtypeCode) {
    const parentCode = $section.attr('data-parent-code');
    if (!parentCode || !subtypeCode) {
        return;
    }
    $section.find('.fg-weight-input').val('');
    $section.find(`[data-fg-code="${parentCode}"]`).val('1');
    $section.find(`[data-fg-code="${subtypeCode}"]`).val('1');
    updateParentSubtypeSection($section);
}

function getSectionValidation($section) {
    const parentCode = $section.attr('data-parent-code');
    if (!parentCode) {
        return { state: 'ok', message: '' };
    }

    const parentVal = parseWeight($section.find(`[data-fg-code="${parentCode}"]`).val());
    const subtypeInputs = $section.find('.fg-subtype-weight');
    const activeSubtypes = subtypeInputs.filter(function hasValue() {
        return parseWeight($(this).val()) > 0;
    });

    if (parentVal <= 0 && activeSubtypes.length) {
        return {
            state: 'error',
            message: (
                'Set the overall parent weight first (usually 1), or use the single feeding type dropdown. '
                + 'A subtype like Predator cannot be saved without Zoophagous.'
            ),
        };
    }
    if (parentVal <= 0) {
        return { state: 'empty', message: 'Not set' };
    }
    if (!activeSubtypes.length) {
        return { state: 'warn', message: 'Parent set — add subtype detail' };
    }

    const values = activeSubtypes.map(function readVal() {
        return parseWeight($(this).val());
    }).get();
    const hasOne = values.some((value) => isOne(value));
    const hasFraction = values.some((value) => value > 0 && !isOne(value));

    if (hasOne && hasFraction) {
        return {
            state: 'error',
            message: 'Do not mix subtype 1 with fractions.',
        };
    }
    if (isOne(parentVal) && hasFraction) {
        const total = values.reduce((sum, value) => sum + value, 0);
        if (Math.abs(total - 1) > TOLERANCE) {
            return {
                state: 'error',
                message: `Subtypes must sum to 1 (now ${total.toFixed(3)})`,
            };
        }
        return { state: 'ok', message: 'Fractional subtypes OK' };
    }
    return { state: 'ok', message: 'OK' };
}

function updateSubtypeSumBar($section) {
    const parentCode = $section.attr('data-parent-code');
    const $bar = $section.find('.fg-subtype-sum .progress-bar');
    const $label = $section.find('.fg-subtype-sum-label');
    const $hint = $section.find('.fg-subtype-hint');

    if (!parentCode) {
        return;
    }

    const parentVal = parseWeight($section.find(`[data-fg-code="${parentCode}"]`).val());
    const subtypeInputs = $section.find('.fg-subtype-weight');
    const values = subtypeInputs.map(function readVal() {
        return parseWeight($(this).val());
    }).get();
    const activeTotal = values.reduce((sum, value) => sum + (value > 0 ? value : 0), 0);
    const activeCount = values.filter((value) => value > 0).length;

    const needsSum = isOne(parentVal) && values.some((value) => value > 0 && !isOne(value));
    const target = needsSum ? 1 : 0;
    const ratio = target > 0 ? Math.min(activeTotal / target, 1) : 0;

    $bar.css('width', `${ratio * 100}%`);
    $bar.removeClass('bg-success bg-warning bg-danger');
    if (!needsSum) {
        $label.text(activeCount ? `${activeCount} subtype(s) set` : '');
        $bar.addClass('bg-secondary');
    } else if (Math.abs(activeTotal - 1) <= TOLERANCE) {
        $label.text(`Subtype sum: ${activeTotal.toFixed(3)} / 1.000`);
        $bar.addClass('bg-success');
    } else {
        $label.text(`Subtype sum: ${activeTotal.toFixed(3)} / 1.000`);
        $bar.addClass(activeTotal > 1 ? 'bg-danger' : 'bg-warning');
    }

    const validation = getSectionValidation($section);
    $hint.text(validation.state === 'error' ? validation.message : '');
    $hint.toggleClass('text-danger', validation.state === 'error');
    $hint.toggleClass('text-muted', validation.state !== 'error');

    const $badge = $section.find('.fg-section-status');
    $badge.removeClass('bg-secondary bg-success bg-warning bg-danger');
    if (validation.state === 'empty') {
        $badge.addClass('bg-secondary').text('Not set');
    } else if (validation.state === 'error') {
        $badge.addClass('bg-danger').text('Fix weights');
    } else if (validation.state === 'warn') {
        $badge.addClass('bg-warning').text('Incomplete');
    } else {
        $badge.addClass('bg-success').text('OK');
    }

    const parentActive = parentVal > 0;
    $section.find('.fg-subtypes-block').toggleClass('fg-subtypes-dimmed', !parentActive);
}

function maybeAutoSetParent($section, $changedInput) {
    const parentCode = $section.attr('data-parent-code');
    if (!parentCode || !$changedInput.hasClass('fg-subtype-weight')) {
        return;
    }
    const subtypeVal = parseWeight($changedInput.val());
    if (subtypeVal <= 0) {
        return;
    }
    const $parentInput = $section.find(`[data-fg-code="${parentCode}"]`).first();
    if (parseWeight($parentInput.val()) > 0) {
        return;
    }
    $parentInput.val('1');
    const $hint = $section.find('.fg-subtype-hint');
    $hint.text(
        'Overall parent auto-set to 1. Lower it (e.g. 0.5) if this is a mixed feeder.',
    );
    $hint.removeClass('text-danger').addClass('text-info');
}

function syncSingleSubtypePicker($section) {
    const parentCode = $section.attr('data-parent-code');
    const $picker = $section.find('.fg-single-subtype-picker');
    if (!parentCode || !$picker.length) {
        return;
    }

    const parentVal = parseWeight($section.find(`[data-fg-code="${parentCode}"]`).val());
    const activeSubtypes = $section.find('.fg-subtype-weight').filter(function active() {
        return parseWeight($(this).val()) > 0;
    });

    if (!isOne(parentVal) || activeSubtypes.length !== 1 || !isOne(activeSubtypes.val())) {
        return;
    }
    $picker.val(activeSubtypes.attr('data-fg-code'));
}

function updateParentSubtypeSection($section) {
    updateSubtypeSumBar($section);
    syncSingleSubtypePicker($section);
}

function initParentSubtypeSection($section) {
    $section.on('click', '.fg-preset', function onPreset() {
        const value = $(this).attr('data-value');
        const parentCode = $section.attr('data-parent-code');
        $section.find(`[data-fg-code="${parentCode}"]`).val(value);
        updateParentSubtypeSection($section);
    });

    $section.on('click', '.fg-clear-section', function onClear() {
        clearSection($section);
    });

    $section.on('change', '.fg-single-subtype-picker', function onPick() {
        const code = $(this).val();
        if (code) {
            applySingleSubtype($section, code);
        }
    });

    $section.on('input', '.fg-weight-input', function onInput() {
        maybeAutoSetParent($section, $(this));
        updateParentSubtypeSection($section);
    });

    updateParentSubtypeSection($section);
}

function initOtherSection($section) {
    $section.on('change', '.fg-other-toggle', function onToggle() {
        const target = $(this).attr('data-target');
        const $input = $(`#id_${target}`);
        if ($(this).is(':checked')) {
            $input.val('1');
        } else {
            $input.val('');
        }
    });
}

$(function initFunctionalGroupWeights() {
    $('.fg-section-parent').each(function initSection() {
        initParentSubtypeSection($(this));
    });
    $('.fg-section-other').each(function initSection() {
        initOtherSection($(this));
    });
});
