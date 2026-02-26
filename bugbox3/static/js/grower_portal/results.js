import Tooltip from 'bootstrap/js/dist/tooltip'

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function(el) {
        new Tooltip(el);
    });

    const json_context = JSON.parse(document.getElementById('json_context').textContent);
    const factorDetailBase = json_context.factor_detail_url;
    const basicResultsUrl = json_context.basic_results_url;
    const yearSelect = document.getElementById('id_year');
    const filterForm = document.getElementById('resultsFilterForm');

    // Individual transect values toggle
    const showIndividualCheckbox = document.getElementById('showIndividualValues');

    function applyIndividualValuesVisibility(scope) {
        const show = showIndividualCheckbox && showIndividualCheckbox.checked;
        (scope || document).querySelectorAll('.individual-values-row').forEach(function(row) {
            row.style.display = show ? '' : 'none';
        });
    }

    if (showIndividualCheckbox) {
        showIndividualCheckbox.addEventListener('change', function() {
            applyIndividualValuesVisibility();
        });
    }

    // Result type accordion filtering
    const resultTypeSelect = document.getElementById('id_result_type');

    function filterAccordions(value) {
        document.querySelectorAll('.accordion-item[data-result-type]').forEach(function(item) {
            item.style.display = (!value || item.dataset.resultType === value) ? '' : 'none';
        });
    }

    filterAccordions(json_context.result_type_filter);

    if (resultTypeSelect) {
        resultTypeSelect.addEventListener('change', function() {
            filterAccordions(this.value);
        });
    }

    // Project type dropdown — only show options available for the selected year
    const yearsToProjectTypes = json_context.years_to_project_types;
    const projectTypeLabels = json_context.project_type_labels;
    const projectTypeSelect = document.getElementById('id_project_type');

    function updateProjectTypeOptions(selectedYear) {
        if (!projectTypeSelect) return;
        const available = yearsToProjectTypes[String(selectedYear)] || [];
        const currentValue = projectTypeSelect.value;

        projectTypeSelect.innerHTML = '';
        const choices = available.length ? available : Object.keys(projectTypeLabels);
        choices.forEach(function(value) {
            const opt = document.createElement('option');
            opt.value = value;
            opt.textContent = projectTypeLabels[value] || value;
            projectTypeSelect.appendChild(opt);
        });

        projectTypeSelect.value = available.includes(currentValue) ? currentValue : (choices[0] || '');
    }

    updateProjectTypeOptions(json_context.year);

    if (yearSelect) {
        yearSelect.addEventListener('change', function() {
            updateProjectTypeOptions(this.value);
            if (filterForm) filterForm.requestSubmit();
        });
    }

    if (projectTypeSelect) {
        projectTypeSelect.addEventListener('change', function() {
            if (filterForm) filterForm.requestSubmit();
        });
    }

    // Event delegation for factor row clicks (works for dynamically-swapped Basic rows too)
    document.addEventListener('click', function(e) {
        if (e.target.closest('[data-bs-toggle="tooltip"]')) return;
        const row = e.target.closest('tr[data-factor-name]');
        if (!row) return;

        const resultType = row.dataset.resultType;
        let depth = '';
        if (resultType === 'basic') {
            const basicContainer = document.getElementById('basic-results-tables');
            depth = basicContainer ? (basicContainer.dataset.depth || '') : '';
        }

        const params = new URLSearchParams({
            year: json_context.year,
            project_type: json_context.project_type,
            result_type: resultType,
            depth: depth,
            factor_name: row.dataset.factorName,
        });
        window.location.href = factorDetailBase + '?' + params.toString();
    });

    // AJAX depth filtering — swap only the Basic tables, no page reload
    const depthSelect = document.getElementById('depthSelect');
    const basicContainer = document.getElementById('basic-results-tables');

    if (depthSelect && basicContainer) {
        depthSelect.addEventListener('change', function() {
            const params = new URLSearchParams({
                year: json_context.year,
                project_type: json_context.project_type,
                depth: depthSelect.value,
            });
            fetch(`${basicResultsUrl}?${params}`)
                .then(r => r.text())
                .then(html => {
                    basicContainer.innerHTML = html;
                    basicContainer.dataset.depth = depthSelect.value;
                    applyIndividualValuesVisibility(basicContainer);
                    basicContainer.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function(el) {
                        new Tooltip(el);
                    });
                });
        });
    }

    // Carry the current depth into full-page filter submissions (year/project_type changes)
    if (filterForm && depthSelect) {
        filterForm.addEventListener('submit', function() {
            let hidden = filterForm.querySelector('input[name="depth"]');
            if (!hidden) {
                hidden = document.createElement('input');
                hidden.type = 'hidden';
                hidden.name = 'depth';
                filterForm.appendChild(hidden);
            }
            hidden.value = depthSelect.value;
        });
    }
});
