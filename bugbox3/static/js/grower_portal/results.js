import ApexCharts from 'apexcharts';
import Tooltip from 'bootstrap/js/dist/tooltip';

function isElementVisible(element) {
    return element && element.offsetParent !== null && element.offsetWidth > 0;
}

function buildFunctionalGroupChartOptions(payload) {
    const rowLabels = payload.rows.map(function(row) {
        return row.label;
    });
    const colors = payload.series_meta.map(function(meta) {
        return meta.color;
    });
    const series = payload.series_meta.map(function(meta) {
        return {
            name: meta.name,
            data: payload.rows.map(function(row) {
                const category = row.categories.find(function(item) {
                    return item.key === meta.key;
                });
                return category && category.percent ? category.percent : 0;
            }),
        };
    });

    const axisPercentLabelStyle = {
        colors: '#111111',
        fontSize: '12px',
        fontWeight: 500,
        fontFamily: 'inherit',
    };
    const axisRowLabelStyle = {
        colors: '#111111',
        fontSize: '13px',
        fontWeight: 600,
        fontFamily: 'inherit',
    };

    return {
        series: series,
        chart: {
            type: 'bar',
            height: Math.max(160, 80 + payload.rows.length * 44),
            stacked: true,
            stackType: '100%',
            toolbar: { show: false },
            fontFamily: 'inherit',
        },
        plotOptions: {
            bar: {
                horizontal: true,
                barHeight: '70%',
                dataLabels: {
                    position: 'center',
                },
            },
        },
        colors: colors,
        grid: {
            borderColor: '#dee2e6',
            xaxis: {
                lines: { show: true },
            },
            yaxis: {
                lines: { show: false },
            },
        },
        xaxis: {
            categories: rowLabels,
            labels: {
                style: axisRowLabelStyle,
                maxWidth: 200,
            },
            axisBorder: {
                show: true,
                color: '#ced4da',
            },
            axisTicks: {
                show: true,
                color: '#ced4da',
            },
        },
        yaxis: {
            min: 0,
            max: 100,
            tickAmount: 5,
            labels: {
                style: axisPercentLabelStyle,
                formatter: function(val) {
                    if (typeof val === 'number' && !Number.isNaN(val)) {
                        return Math.round(val) + '%';
                    }
                    return val;
                },
            },
            axisBorder: {
                show: true,
                color: '#ced4da',
            },
        },
        legend: {
            position: 'bottom',
            horizontalAlign: 'center',
        },
        dataLabels: {
            enabled: true,
            formatter: function(val, opts) {
                const meta = payload.series_meta[opts.seriesIndex];
                const row = payload.rows[opts.dataPointIndex];
                const category = row.categories.find(function(item) {
                    return item.key === meta.key;
                });
                if (!category || !category.percent || val == null || val < 3) {
                    return '';
                }
                if (val < 10) {
                    return val.toFixed(1) + '%';
                }
                return Math.round(val) + '%';
            },
            style: {
                fontSize: '11px',
                colors: ['#ffffff', '#ffffff', '#ffffff', '#212121'],
            },
            dropShadow: {
                enabled: false,
            },
        },
        tooltip: {
            shared: false,
            intersect: true,
            custom: function({ seriesIndex, dataPointIndex }) {
                const meta = payload.series_meta[seriesIndex];
                const row = payload.rows[dataPointIndex];
                const category = row.categories.find(function(item) {
                    return item.key === meta.key;
                });
                if (!category || !category.percent) {
                    return '';
                }
                return (
                    '<div class="apexcharts-tooltip-title" style="font-family: inherit;">' +
                    row.label +
                    '</div>' +
                    '<div class="apexcharts-tooltip-series-group apexcharts-active" style="display: flex;">' +
                    '<span class="apexcharts-tooltip-marker" style="background-color: ' +
                    category.color +
                    ';"></span>' +
                    '<div class="apexcharts-tooltip-text">' +
                    '<div class="apexcharts-tooltip-y-group">' +
                    '<span class="apexcharts-tooltip-text-y-label"></span>' +
                    '<span class="apexcharts-tooltip-text-y-value">' +
                    category.label +
                    ': ' +
                    category.count +
                    ' (' +
                    category.percent +
                    '%)' +
                    '</span></div></div></div>'
                );
            },
        },
    };
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function(el) {
        new Tooltip(el);
    });

    const json_context = JSON.parse(document.getElementById('json_context').textContent);
    const factorDetailBase = json_context.factor_detail_url;
    const basicResultsUrl = json_context.basic_results_url;
    const yearSelect = document.getElementById('id_year');
    const filterForm = document.getElementById('resultsFilterForm');

    let functionalGroupChart = null;
    let functionalGroupChartRendered = false;

    function renderFunctionalGroupChart() {
        const payload = json_context.insect_functional_group_chart;
        if (!payload || !payload.rows || !payload.rows.length) {
            return;
        }

        const element = document.getElementById(payload.element_id);
        if (!element || !isElementVisible(element)) {
            return;
        }

        if (functionalGroupChart) {
            functionalGroupChart.destroy();
            functionalGroupChart = null;
            functionalGroupChartRendered = false;
        }

        functionalGroupChart = new ApexCharts(
            element,
            buildFunctionalGroupChartOptions(payload),
        );
        functionalGroupChart.render().then(function() {
            functionalGroupChartRendered = true;
        });
    }

    function tryRenderFunctionalGroupChart() {
        if (!json_context.insect_functional_group_chart) {
            return;
        }
        if (functionalGroupChartRendered && functionalGroupChart) {
            functionalGroupChart.updateOptions({}, false, true);
            return;
        }
        renderFunctionalGroupChart();
    }

    tryRenderFunctionalGroupChart();

    document.getElementById('categoryTabs')?.addEventListener('shown.bs.tab', function() {
        window.setTimeout(tryRenderFunctionalGroupChart, 50);
    });

    document.getElementById('categoryTabsContent')?.addEventListener('shown.bs.collapse', function() {
        window.setTimeout(tryRenderFunctionalGroupChart, 50);
    });

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
        const depthSelect = document.getElementById('depthSelect-' + resultType);
        if (depthSelect) {
            depth = depthSelect.value || '';
        } else if (resultType === 'basic') {
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

    const basicDepthSelect = document.getElementById('depthSelect-basic');
    const basicContainer = document.getElementById('basic-results-tables');

    if (basicDepthSelect && basicContainer) {
        basicDepthSelect.addEventListener('change', function() {
            const params = new URLSearchParams({
                year: json_context.year,
                project_type: json_context.project_type,
                depth: basicDepthSelect.value,
            });
            fetch(`${basicResultsUrl}?${params}`)
                .then(r => r.text())
                .then(html => {
                    basicContainer.innerHTML = html;
                    basicContainer.dataset.depth = basicDepthSelect.value;
                    applyIndividualValuesVisibility(basicContainer);
                    basicContainer.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function(el) {
                        new Tooltip(el);
                    });
                });
        });
    }

    document.querySelectorAll('.depth-select').forEach(function(select) {
        if (select.id === 'depthSelect-basic') return;
        select.addEventListener('change', function() {
            const params = new URLSearchParams(window.location.search);
            params.set('depth', this.value);
            window.location.search = params.toString();
        });
    });

    // Carry the current depth into full-page filter submissions (year/project_type changes)
    const anyDepthSelect = document.querySelector('.depth-select');
    if (filterForm && anyDepthSelect) {
        filterForm.addEventListener('submit', function() {
            let hidden = filterForm.querySelector('input[name="depth"]');
            if (!hidden) {
                hidden = document.createElement('input');
                hidden.type = 'hidden';
                hidden.name = 'depth';
                filterForm.appendChild(hidden);
            }
            const selectedDepth = document.querySelector('.depth-select')?.value || '';
            hidden.value = selectedDepth;
        });
    }
});
