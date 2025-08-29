import $ from 'jquery';

$(document).ready(function () {
    const $lat = $('#id_latitude');
    const $lon = $('#id_longitude');
    const $state = $('#id_state_region');
    const $county = $('#id_county_region');

    function updateRegionFields() {
        const lat = $lat.val();
        const lon = $lon.val();

        if (lat && lon) {
            $.ajax({
                url: '/samples/ajax/get-region/',
                data: { lat, lon },
                success: function (data) {
                    $state.val(data.state || '');
                    $county.val(data.county || '');
                },
                error: function () {
                    $state.val('');
                    $county.val('');
                }
            });
        }
    }

    $lat.on('change', updateRegionFields);
    $lon.on('change', updateRegionFields);
});
