import $ from 'jquery';
import DataTable from 'datatables.net-bs5';
import { Tooltip} from 'bootstrap'



$(function () {
    const json_context = JSON.parse(document.getElementById('json_context').textContent);
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new Tooltip(tooltipTriggerEl))

    function bbNorm(s) {
        return (s || "").toString().trim().toLowerCase();
    }

    function bbUpdateCounts(root) {
        const select = root.querySelector("[data-bb-select]");
        const count = root.querySelector("[data-bb-count]");
        if (!select || !count) return;

        const opts = Array.from(select.options);
        const visible = opts.filter(o => !o.hidden);
        const selectedVisible = visible.filter(o => o.selected);
        count.textContent = `${selectedVisible.length} selected (of ${visible.length} shown)`;
    }

    function bbApplyFilter(root, q) {
        const select = root.querySelector("[data-bb-select]");
        if (!select) return;

        const query = bbNorm(q);
        for (const opt of Array.from(select.options)) {
            opt.hidden = query.length > 0 && !bbNorm(opt.textContent).includes(query);
        }
        bbUpdateCounts(root);
    }

    function bbSelectVisible(root, shouldSelect) {
        const select = root.querySelector("[data-bb-select]");
        if (!select) return;
        for (const opt of Array.from(select.options)) {
            if (opt.hidden) continue;
            opt.selected = shouldSelect;
        }
        select.dispatchEvent(new Event("change", { bubbles: true }));
        bbUpdateCounts(root);
    }

    function bbWireMultiselect(root) {
        const filter = root.querySelector("[data-bb-filter]");
        const select = root.querySelector("[data-bb-select]");
        const allBtn = root.querySelector("[data-bb-select-all]");
        const noneBtn = root.querySelector("[data-bb-select-none]");

        if (filter) {
            filter.addEventListener("input", () => bbApplyFilter(root, filter.value));
        }
        if (select) {
            select.addEventListener("change", () => bbUpdateCounts(root));
        }
        if (allBtn) allBtn.addEventListener("click", () => bbSelectVisible(root, true));
        if (noneBtn) noneBtn.addEventListener("click", () => bbSelectVisible(root, false));

        bbUpdateCounts(root);
    }

    document.querySelectorAll("[data-bb-multiselect]").forEach(bbWireMultiselect);

    function getDetail( row ) {
        return row.detail_row
    }

    document.querySelector('#check-all_habitats')?.addEventListener('change', (e) => {
        document.querySelectorAll('[name=habitats]').forEach(el => el.checked = e.target.checked);
    });

    document.querySelector('#check-all_countries')?.addEventListener('change', (e) => {
        document.querySelectorAll('[name=countries]').forEach(el => el.checked = e.target.checked);
    });

    document.querySelector('#check-all_states')?.addEventListener('change', (e) => {
        document.querySelectorAll('[name=states]').forEach(el => el.checked = e.target.checked);
    });

    document.querySelector('#check-all_sampleTypes3')?.addEventListener('change', (e) => {
        document.querySelectorAll('[name=sampleTypes]').forEach(el => el.checked = e.target.checked);
    });

    document.querySelector('#check-all_location_indices')?.addEventListener('change', (e) => {
        document.querySelectorAll('input[name="indices"]').forEach(el => {
        el.checked = e.target.checked;
    });
    });
    document.querySelector('#exportForm3')?.addEventListener('submit', function () {
    const statusDiv = document.querySelector('#location-export-status');
    if (statusDiv) {
        statusDiv.textContent = 'Exporting Filtered File... 0%';
    }

    setTimeout(() => pollLocationExportProgress(json_context.experiment.id), 1500);
    });

    function pollLocationExportProgress(experimentId) {
        const statusDiv = document.querySelector('#location-export-status');

        fetch(`/samples/export-by-location-progress/${experimentId}/`)
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    statusDiv.textContent = 'Generating Download Link...';
                    location.reload();
                } else if (data.status === 'error') {
                    statusDiv.textContent = 'Export Failed';
                } else {
                    statusDiv.textContent = `Exporting Filtered File... ${data.progress}%`;
                    setTimeout(() => pollLocationExportProgress(experimentId), 2000);
                }
            })
            .catch(() => {
                statusDiv.textContent = 'Error checking export progress';
            });
    }

    if (json_context.last_location_exported_file_status === 'pending') {
    pollLocationExportProgress(json_context.experiment.id);
    }

    const checkAllSampleTypes = document.querySelector('#check-all_sampleTypes');
    if (checkAllSampleTypes) {
        checkAllSampleTypes.onchange = (e) => {
            document.querySelectorAll('[name=sampleTypes]').forEach(el => {
                el.checked = e.target.checked
            })
        }
    }
    const checkAllSampleTypes2 = document.querySelector('#check-all_sampleTypes2');
    if (checkAllSampleTypes2) {
        checkAllSampleTypes2.onchange = (e) => {
            document.querySelectorAll('[name=sampleTypes2]').forEach(el => {
                el.checked = e.target.checked
            })
        }
    }
    const checkAllIndices = document.querySelector('#check-all_indices');
    if (checkAllIndices) {
        checkAllIndices.onchange = (e) => {
            document.querySelectorAll('[name=indices]').forEach(el => {
                el.checked = e.target.checked
            })
        }
    }

    var samples_table = $('#samples-table').DataTable({
        order: [[1, 'desc']],
        pageLength: 25,
        ordering: false,
        processing: true,
        serverSide: true,
        ajax: {
            url: json_context.sites_datatables_url,
            dataSrc: 'data'
        },
        language: {
            searchPlaceholder: "Search"
        },
        preDrawCallback: function (settings) {
            var api = new $.fn.dataTable.Api(settings);
            var pagination = $(this)
                .closest('.dataTables_wrapper')
                .find('.dataTables_paginate');
            pagination.toggle(api.page.info().pages > 1);
        },
        columns: [
            {
                class: 'details-control',
                orderable: false,
                data: null,
                defaultContent: '',
            },
            {
                data: 'data_row',
            }
        ]
    });

    // Array to track the ids of the details displayed rows
    var detailRows = [];
    $('#samples-table tbody').on( 'click', 'tr td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = samples_table.row(tr);
        var idx = detailRows.indexOf(tr.attr('id'));

        if (row.child.isShown()) {
            tr.removeClass('details');
            row.child.hide();

            // Remove from the 'open' array
            detailRows.splice(idx, 1);
        } else {
            tr.addClass('details');
            row.child(getDetail(row.data())).show();

            // Add to the 'open' array
            if (idx === -1) {
                detailRows.push(tr.attr('id'));
            }
        }
    });
    // On each draw, loop over the `detailRows` array and show any child rows
    samples_table.on('draw', function () {
        detailRows.forEach(function(id, i) {
            $('#' + id + ' td.details-control').trigger('click');
        });
    });

    const excludedModal = document.getElementById('excludedFromIndicesModal');
    let parentModalId = null;
    
    if (excludedModal) {
        const infoIcons = document.querySelectorAll('[data-bs-target="#excludedFromIndicesModal"]');
        infoIcons.forEach(icon => {
            icon.addEventListener('click', function() {
                const parentModal = this.closest('.modal');
                if (parentModal) {
                    parentModalId = parentModal.id;
                }
            });
        });
        
        excludedModal.addEventListener('hidden.bs.modal', function () {
            if (parentModalId) {
                const parentModal = document.getElementById(parentModalId);
                if (parentModal) {
                    setTimeout(function() {
                        parentModal.classList.add('show');
                        parentModal.style.display = 'block';
                        parentModal.setAttribute('aria-modal', 'true');
                        parentModal.removeAttribute('aria-hidden');
                        
                        document.body.classList.add('modal-open');
                        
                        let backdrop = document.querySelector('.modal-backdrop');
                        if (!backdrop) {
                            backdrop = document.createElement('div');
                            backdrop.className = 'modal-backdrop fade show';
                            document.body.appendChild(backdrop);
                        }
                    }, 150);
                    
                    parentModalId = null;
                }
            }
        });
    }

})
