/**
 * Data Ingestion Hub Admin JS
 *  Category card selection (highlight selected, populate hidden input)
 *  Fetch valid result_types for selected category via AJAX
 *  Show/hide upload form wrapper once a category is chosen
 *  Client-side validation feedback
 *  Year default to current year
 */

document.addEventListener('DOMContentLoaded', function () {
    const ctx = JSON.parse(
        document.getElementById('json_context')?.textContent || '{}'
    );
    const categoryResultTypesUrl = ctx.categoryResultTypesUrl || '';

    const categoryInput   = document.getElementById('id_category');
    const resultTypeSelect = document.getElementById('id_result_type');
    const uploadFormWrapper = document.getElementById('uploadFormWrapper');
    const categoryCards   = document.querySelectorAll('.category-card');
    const fileInput       = document.getElementById('id_data_file');
    const fileHelpText    = document.getElementById('fileHelpText');
    const yearSelect      = document.getElementById('id_year');

    // default year to current year
    if (yearSelect) {
        const currentYear = new Date().getFullYear().toString();
        for (const opt of yearSelect.options) {
            if (opt.value === currentYear) {
                opt.selected = true;
                break;
            }
        }
    }

    // category card selection
    function selectCategory(value) {
        if (!value) return;

        categoryCards.forEach(function (card) {
            const isSelected = card.dataset.category === value;
            card.classList.toggle('selected', isSelected);
            card.classList.toggle('btn-primary', isSelected);
            card.classList.toggle('text-white', isSelected);
            card.classList.toggle('btn-outline-secondary', !isSelected);
        });

        if (categoryInput) categoryInput.value = value;

        // fetch result types for this category
        fetchResultTypes(value);
    }

    categoryCards.forEach(function (card) {
        card.addEventListener('click', function () {
            selectCategory(card.dataset.category);
        });
    });

    // AJAX: load result_types for selected category
    function fetchResultTypes(category) {
        if (!categoryResultTypesUrl || !resultTypeSelect) return;

        resultTypeSelect.innerHTML = '<option value="">Loading…</option>';
        resultTypeSelect.disabled = true;

        fetch(`${categoryResultTypesUrl}?category=${encodeURIComponent(category)}`)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                resultTypeSelect.innerHTML = '';
                if (!data.result_types || !data.result_types.length) {
                    resultTypeSelect.innerHTML = '<option value="">No data types available</option>';
                    return;
                }
                data.result_types.forEach(function (rt) {
                    const opt = document.createElement('option');
                    opt.value = rt.value;
                    opt.textContent = rt.label;
                    resultTypeSelect.appendChild(opt);
                });
                resultTypeSelect.disabled = false;

                // Update file-help text for birds
                updateFileHelp(category);

                // Show form
                if (uploadFormWrapper) {
                    uploadFormWrapper.classList.remove('d-none');
                    uploadFormWrapper.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            })
            .catch(function (err) {
                console.error('Failed to load result types:', err);
                resultTypeSelect.innerHTML = '<option value="">Error loading types</option>';
                resultTypeSelect.disabled = false;
            });
    }

    function updateFileHelp(category) {
        if (!fileHelpText) return;
        if (category === 'birds') {
            fileHelpText.textContent =
                'Excel (.xlsx) file with row 1 = family headers, row 2 = column headers ' +
                '(must include Site Code, Abundance, Richness), row 3+ = survey data.';
            if (fileInput) fileInput.accept = '.xlsx,.xls,.csv';
        } else {
            fileHelpText.textContent = 'CSV file (≤ 10 MB). Must include the required sample code column.';
            if (fileInput) fileInput.accept = '.csv';
        }
    }

    // auto-select if category was pre-filled
    const preSelected = ctx.selectedCategory || (categoryInput && categoryInput.value) || '';
    if (preSelected) {
        selectCategory(preSelected);
    } else {
        // style all cards as unselected by default
        categoryCards.forEach(function (card) {
            card.classList.add('btn-outline-secondary');
        });
    }

    // basic client-side submit validation
    const form = document.getElementById('dataIngestionForm');
    if (form) {
        form.addEventListener('submit', function (e) {
            let valid = true;

            if (!categoryInput || !categoryInput.value) {
                e.preventDefault();
                valid = false;
                showAlert('Please select a category before uploading.');
            }

            if (valid && resultTypeSelect && !resultTypeSelect.value) {
                e.preventDefault();
                showAlert('Please select a data type.');
            }

            if (valid && fileInput && !fileInput.files.length) {
                e.preventDefault();
                showAlert('Please choose a file to upload.');
            }
        });
    }

    function showAlert(message) {
        // remove existing transient alerts
        document.querySelectorAll('.ingestion-alert-temp').forEach(function (el) { el.remove(); });
        const div = document.createElement('div');
        div.className = 'alert alert-warning alert-dismissible fade show ingestion-alert-temp mt-3';
        div.setAttribute('role', 'alert');
        div.innerHTML =
            `<i class="fas fa-exclamation-triangle me-2"></i>${message}` +
            '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
        if (form) form.before(div);
    }
});
