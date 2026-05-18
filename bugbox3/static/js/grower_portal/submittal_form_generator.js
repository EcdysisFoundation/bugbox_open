document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('submittal-form');
    if (!form) {
        return;
    }

    const apiUrl = form.getAttribute('data-submittal-generations-url');
    const projectSelect = document.getElementById('id_submittal_project_type');
    const clusterInput = document.getElementById('id_cluster_number');
    const yearInput = document.getElementById('id_year');
    const generationSelect = document.getElementById('id_label_generation_id');
    const codesPanel = document.getElementById('submittal-codes-panel');
    const codesContainer = document.getElementById('submittal-codes-container');
    const codesEmpty = document.getElementById('submittal-codes-empty');
    const codesLoading = document.getElementById('submittal-codes-loading');
    const selectAllBtn = document.getElementById('submittal-select-all-codes');
    const selectNoneBtn = document.getElementById('submittal-select-none-codes');
    const forageHint = document.getElementById('submittal-forage-hint');

    let generationsById = {};

    function setLoading(loading) {
        if (codesLoading) {
            codesLoading.style.display = loading ? 'block' : 'none';
        }
    }

    function resetCodesUi(message) {
        if (codesContainer) {
            codesContainer.innerHTML = '';
        }
        if (codesPanel) {
            codesPanel.style.display = 'none';
        }
        if (codesEmpty) {
            codesEmpty.style.display = message ? 'block' : 'none';
            codesEmpty.textContent = message || '';
        }
        if (forageHint) {
            forageHint.style.display = 'none';
            forageHint.textContent = '';
            forageHint.className = 'alert alert-info mt-2';
        }
        generationsById = {};
    }

    function renderGenerationOptions(generations) {
        if (!generationSelect) {
            return;
        }
        generationSelect.innerHTML = '';
        const placeholder = document.createElement('option');
        placeholder.value = '';
        placeholder.textContent = generations.length
            ? '-- Select a label generation --'
            : 'No ready inner label generations found for this project/cluster/year';
        generationSelect.appendChild(placeholder);

        generations.forEach(function (gen) {
            const opt = document.createElement('option');
            opt.value = String(gen.id);
            opt.textContent =
                '#' + gen.id + ' — ' + gen.generated_at +
                ' — ' + gen.code_count + ' code(s)' +
                (gen.has_forage ? ' — includes forage' : '');
            generationSelect.appendChild(opt);
        });
    }

    function renderCodeCheckboxes(gen) {
        if (!codesContainer || !codesPanel) {
            return;
        }
        codesContainer.innerHTML = '';

        gen.codes.forEach(function (code) {
            const col = document.createElement('div');
            col.className = 'col-md-2 col-sm-3 col-4 mb-2';

            const wrap = document.createElement('div');
            wrap.className = 'form-check';

            const input = document.createElement('input');
            input.type = 'checkbox';
            input.className = 'form-check-input submittal-code-checkbox';
            input.name = 'selected_codes';
            input.value = code;
            input.id = 'submittal_code_' + String(code).replace(/[^a-zA-Z0-9_-]/g, '_');
            input.checked = true;

            const label = document.createElement('label');
            label.className = 'form-check-label';
            label.htmlFor = input.id;
            label.textContent = code;

            wrap.appendChild(input);
            wrap.appendChild(label);
            col.appendChild(wrap);
            codesContainer.appendChild(col);
        });

        codesPanel.style.display = 'block';
        if (codesEmpty) {
            codesEmpty.style.display = 'none';
        }

        if (forageHint) {
            forageHint.style.display = 'block';
            if (gen.has_forage) {
                forageHint.className = 'alert alert-info mt-2';
                forageHint.textContent =
                    'This batch includes forage. Plant submittal rows will use your selected codes.';
            } else {
                forageHint.className = 'alert alert-warning mt-2';
                forageHint.textContent =
                    'This batch does not include forage sample types. Uncheck Plant submittal unless you use a forage label batch.';
            }
        }
    }

    function onGenerationChange() {
        const id = generationSelect ? generationSelect.value : '';
        if (!id || !generationsById[id]) {
            if (codesPanel) {
                codesPanel.style.display = 'none';
            }
            if (codesContainer) {
                codesContainer.innerHTML = '';
            }
            return;
        }
        renderCodeCheckboxes(generationsById[id]);
    }

    function hasServerRenderedCodes() {
        return codesContainer && codesContainer.querySelector('input[name="selected_codes"]');
    }

    function loadGenerations(options) {
        const preserveCodes = options && options.preserveCodes;
        if (!apiUrl || !projectSelect || !clusterInput || !yearInput) {
            return;
        }
        const projectType = projectSelect.value.trim();
        const cluster = clusterInput.value.trim();
        const year = yearInput.value.trim();

        if (!preserveCodes) {
            resetCodesUi('');
        }
        if (generationSelect && !preserveCodes) {
            generationSelect.innerHTML = '<option value="">-- Enter cluster, year, and project --</option>';
        }

        if (!projectType || !cluster || !year) {
            resetCodesUi('Enter project, cluster, and year, then tab out of the year field to load label batches.');
            return;
        }

        setLoading(true);
        const url =
            apiUrl +
            '?project_type=' + encodeURIComponent(projectType) +
            '&cluster=' + encodeURIComponent(cluster) +
            '&year=' + encodeURIComponent(year);

        fetch(url)
            .then(function (response) {
                return response.json();
            })
            .then(function (data) {
                const generations = data.generations || [];
                const previousGenId = generationSelect ? generationSelect.value : '';
                generationsById = {};
                generations.forEach(function (gen) {
                    generationsById[String(gen.id)] = gen;
                });
                renderGenerationOptions(generations);
                if (generations.length === 0) {
                    resetCodesUi(
                        'No ready inner label generations with codes found. Generate inner labels first.'
                    );
                    return;
                }
                if (previousGenId && generationsById[previousGenId]) {
                    generationSelect.value = previousGenId;
                } else if (generationSelect.options.length === 2) {
                    generationSelect.selectedIndex = 1;
                }
                if (!preserveCodes) {
                    onGenerationChange();
                } else if (codesPanel) {
                    codesPanel.style.display = 'block';
                }
            })
            .catch(function () {
                resetCodesUi('Could not load label generations. Try again.');
            })
            .finally(function () {
                setLoading(false);
            });
    }

    function setAllCodes(checked) {
        if (!codesContainer) {
            return;
        }
        codesContainer.querySelectorAll('input[name="selected_codes"]').forEach(function (el) {
            el.checked = checked;
        });
    }

    if (selectAllBtn) {
        selectAllBtn.addEventListener('click', function (e) {
            e.preventDefault();
            setAllCodes(true);
        });
    }
    if (selectNoneBtn) {
        selectNoneBtn.addEventListener('click', function (e) {
            e.preventDefault();
            setAllCodes(false);
        });
    }
    if (generationSelect) {
        generationSelect.addEventListener('change', onGenerationChange);
    }
    if (projectSelect) {
        projectSelect.addEventListener('change', loadGenerations);
    }
    if (clusterInput) {
        clusterInput.addEventListener('blur', loadGenerations);
    }
    if (yearInput) {
        yearInput.addEventListener('blur', loadGenerations);
    }

    if (projectSelect && projectSelect.value && clusterInput && clusterInput.value && yearInput && yearInput.value) {
        loadGenerations({ preserveCodes: hasServerRenderedCodes() });
    } else {
        resetCodesUi('Enter project, cluster, and year, then tab out of the year field to load label batches.');
    }
});
