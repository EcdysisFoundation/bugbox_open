import { bootstrapGoogleMapsFromContext } from './google_maps_api_loader';

const MAX_TRANSECT_SLOTS = 4;

let map;
let markers = [];
let loadingCircle = null;
let loadingOverlay = null;

function getTransectSlot(transect) {
    return transect.slot || (transect.index + 1);
}

function parseCoordinate(value) {
    if (value === null || value === undefined || String(value).trim() === '') {
        return null;
    }
    const parsed = parseFloat(value);
    return Number.isFinite(parsed) ? parsed : null;
}

function setRowVisible(slot, visible) {
    const row = document.querySelector(`.transect-location-row[data-slot="${slot}"]`);
    if (!row) {
        return;
    }
    row.classList.toggle('transect-location-row--hidden', !visible);
}

function updateTransectRowVisibility() {
    for (let slot = 1; slot <= MAX_TRANSECT_SLOTS; slot++) {
        setRowVisible(slot, true);
    }
}

window.initMap = function() {
    const jsonContextElement = document.getElementById('json_context');
    if (!jsonContextElement) {
        console.error('json_context element not found!');
        return;
    }

    let jsonContext;
    try {
        jsonContext = JSON.parse(jsonContextElement.textContent);
    } catch (e) {
        console.error('Error parsing JSON context:', e);
        console.error('JSON content:', jsonContextElement.textContent);
        return;
    }

    let initialCenter = { lat: 37.7749, lng: -122.4194 };
    let initialZoom = 10;

    const transectData = jsonContext.transectData || [];
    if (transectData.length > 0) {
        const validTransects = transectData.filter(
            (t) => parseCoordinate(t.latitude) !== null && parseCoordinate(t.longitude) !== null,
        );
        if (validTransects.length > 0) {
            const avgLat = validTransects.reduce((sum, t) => sum + t.latitude, 0) / validTransects.length;
            const avgLng = validTransects.reduce((sum, t) => sum + t.longitude, 0) / validTransects.length;
            initialCenter = { lat: avgLat, lng: avgLng };
            initialZoom = 17;
        }
    }

    map = new google.maps.Map(document.getElementById('map'), {
        center: initialCenter,
        zoom: initialZoom,
        mapTypeId: 'hybrid',
        mapTypeControl: true,
        mapTypeControlOptions: {
            style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
            position: google.maps.ControlPosition.TOP_RIGHT,
        },
        zoomControl: true,
        streetViewControl: false,
        fullscreenControl: true,
    });

    const locateButton = document.getElementById('locateMe');
    if (locateButton) {
        locateButton.addEventListener('click', handleLocateMe);
    }

    transectData.forEach((transect) => {
        const slot = getTransectSlot(transect);
        const latField = document.getElementById(`id_transect_${slot}_latitude`);
        const lngField = document.getElementById(`id_transect_${slot}_longitude`);
        if (latField && lngField && transect.latitude && transect.longitude) {
            latField.value = transect.latitude;
            lngField.value = transect.longitude;
        }
    });

    setupTransectCodeMonitoring();
};

function handleLocateMe() {
    if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser.');
        return;
    }

    const locateButton = document.getElementById('locateMe');
    locateButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Locating...';
    locateButton.disabled = true;

    loadingCircle = new google.maps.Circle({
        strokeColor: '#2196F3',
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: '#2196F3',
        fillOpacity: 0.15,
        map: map,
        center: map.getCenter(),
        radius: 50,
    });

    loadingOverlay = new google.maps.OverlayView();
    loadingOverlay.onAdd = function() {
        const div = document.createElement('div');
        div.style.position = 'absolute';
        div.style.backgroundColor = '#2196F3';
        div.style.color = 'white';
        div.style.padding = '8px 16px';
        div.style.borderRadius = '20px';
        div.style.fontSize = '14px';
        div.style.fontWeight = 'bold';
        div.style.boxShadow = '0 2px 6px rgba(0,0,0,0.3)';
        div.style.border = '2px solid white';
        div.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Locating...';

        const panes = this.getPanes();
        panes.floatPane.appendChild(div);
        this.div = div;
    };

    loadingOverlay.draw = function() {
        const projection = this.getProjection();
        const center = loadingCircle.getCenter();
        const point = projection.fromLatLngToDivPixel(center);

        if (this.div && point) {
            this.div.style.left = (point.x - this.div.offsetWidth / 2) + 'px';
            this.div.style.top = (point.y - this.div.offsetHeight / 2) + 'px';
        }
    };

    loadingOverlay.onRemove = function() {
        if (this.div) {
            this.div.parentNode.removeChild(this.div);
            this.div = null;
        }
    };

    loadingOverlay.setMap(map);

    let growing = true;
    const pulseInterval = setInterval(() => {
        if (loadingCircle) {
            const currentRadius = loadingCircle.getRadius();
            if (growing) {
                loadingCircle.setRadius(currentRadius + 5);
                if (currentRadius >= 100) growing = false;
            } else {
                loadingCircle.setRadius(currentRadius - 5);
                if (currentRadius <= 50) growing = true;
            }
        } else {
            clearInterval(pulseInterval);
        }
    }, 100);

    navigator.geolocation.getCurrentPosition(
        function(position) {
            const location = {
                lat: position.coords.latitude,
                lng: position.coords.longitude,
            };

            if (loadingCircle) {
                loadingCircle.setMap(null);
                loadingCircle = null;
            }
            if (loadingOverlay) {
                loadingOverlay.setMap(null);
                loadingOverlay = null;
            }
            clearInterval(pulseInterval);

            map.setCenter(location);
            map.setZoom(18);

            locateButton.innerHTML = '<i class="fas fa-check"></i> Located!';
            locateButton.classList.remove('btn-primary');
            locateButton.classList.add('btn-success');

            setTimeout(() => {
                locateButton.innerHTML = '<i class="fas fa-crosshairs"></i> Locate Me';
                locateButton.classList.remove('btn-success');
                locateButton.classList.add('btn-primary');
                locateButton.disabled = false;
            }, 2000);
        },
        function(error) {
            if (loadingCircle) {
                loadingCircle.setMap(null);
                loadingCircle = null;
            }
            if (loadingOverlay) {
                loadingOverlay.setMap(null);
                loadingOverlay = null;
            }
            clearInterval(pulseInterval);

            console.error('Geolocation error:', error);
            let errorMessage = 'Unable to get your location. ';
            if (error.code === error.PERMISSION_DENIED) {
                errorMessage += 'Please enable location permissions in your browser.';
            } else if (error.code === error.POSITION_UNAVAILABLE) {
                errorMessage += 'Location information is unavailable.';
            } else if (error.code === error.TIMEOUT) {
                errorMessage += 'Location request timed out.';
            }
            alert(errorMessage);
            locateButton.innerHTML = '<i class="fas fa-crosshairs"></i> Locate Me';
            locateButton.disabled = false;
        },
        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0,
        },
    );
}

function handleCoordinatePaste(event, slot) {
    const pasted = (event.clipboardData || window.clipboardData).getData('text');
    const match = pasted.match(
        /^\s*(-?\d+(?:\.\d+)?)\s*[,;\s]\s*(-?\d+(?:\.\d+)?)\s*$/,
    );
    if (!match) {
        return;
    }

    event.preventDefault();
    const latField = document.getElementById(`id_transect_${slot}_latitude`);
    const lngField = document.getElementById(`id_transect_${slot}_longitude`);
    if (latField) {
        latField.value = match[1];
    }
    if (lngField) {
        lngField.value = match[2];
    }
    handleTransectFieldChange();
}

function setupTransectCodeMonitoring() {
    for (let slot = 1; slot <= MAX_TRANSECT_SLOTS; slot++) {
        const fieldIds = [
            `id_transect_code_${slot}`,
            `id_transect_${slot}_latitude`,
            `id_transect_${slot}_longitude`,
        ];
        fieldIds.forEach((inputId) => {
            const element = document.getElementById(inputId);
            if (element) {
                element.addEventListener('input', handleTransectFieldChange);
                element.addEventListener('change', handleTransectFieldChange);
            }
        });

        const latField = document.getElementById(`id_transect_${slot}_latitude`);
        const lngField = document.getElementById(`id_transect_${slot}_longitude`);
        if (latField) {
            latField.addEventListener('paste', (event) => handleCoordinatePaste(event, slot));
        }
        if (lngField) {
            lngField.addEventListener('paste', (event) => handleCoordinatePaste(event, slot));
        }
    }

    handleTransectFieldChange();
}

function handleTransectFieldChange() {
    updateTransectRowVisibility();
    updateTransectMarkers();
}

function getTransectsForMap() {
    const transects = [];
    for (let slot = 1; slot <= MAX_TRANSECT_SLOTS; slot++) {
        const latField = document.getElementById(`id_transect_${slot}_latitude`);
        const lngField = document.getElementById(`id_transect_${slot}_longitude`);
        const codeEl = document.getElementById(`id_transect_code_${slot}`);
        const lat = latField ? parseCoordinate(latField.value) : null;
        const lng = lngField ? parseCoordinate(lngField.value) : null;

        if (lat === null || lng === null) {
            continue;
        }

        const code = codeEl && codeEl.value.trim();
        transects.push({
            slot,
            code: code || `Location ${slot}`,
            displayCode: code,
        });
    }
    return transects;
}

function countEnteredTransectCodes() {
    let count = 0;
    for (let slot = 1; slot <= MAX_TRANSECT_SLOTS; slot++) {
        const codeEl = document.getElementById(`id_transect_code_${slot}`);
        if (codeEl && codeEl.value.trim()) {
            count++;
        }
    }
    return count;
}

function updateTransectMarkers() {
    if (!map) {
        return;
    }

    markers.forEach((marker) => {
        marker.setMap(null);
        if (marker.overlay) {
            marker.overlay.setMap(null);
        }
    });
    markers = [];

    const markerColors = ['#FF5252', '#2196F3', '#FFC107', '#9C27B0'];
    const markerLabels = ['1', '2', '3', '4'];
    const bounds = new google.maps.LatLngBounds();
    const transects = getTransectsForMap();

    transects.forEach((transect) => {
        const { slot, code, displayCode } = transect;
        const latField = document.getElementById(`id_transect_${slot}_latitude`);
        const lngField = document.getElementById(`id_transect_${slot}_longitude`);
        const lat = parseCoordinate(latField.value);
        const lng = parseCoordinate(lngField.value);
        const position = { lat, lng };
        const colorIndex = (slot - 1) % markerColors.length;

        const marker = new google.maps.Marker({
            position: position,
            map: map,
            title: `Transect ${code}`,
            draggable: true,
            icon: {
                path: google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
                scale: 6,
                fillColor: markerColors[colorIndex],
                fillOpacity: 1,
                strokeColor: '#000000',
                strokeWeight: 2,
            },
            label: {
                text: markerLabels[colorIndex],
                color: 'white',
                fontSize: '14px',
                fontWeight: 'bold',
            },
        });

        const overlay = new google.maps.OverlayView();
        overlay.onAdd = function() {
            const div = document.createElement('div');
            div.style.position = 'absolute';
            div.style.backgroundColor = markerColors[colorIndex];
            div.style.color = 'white';
            div.style.padding = '4px 8px';
            div.style.borderRadius = '4px';
            div.style.fontSize = '11px';
            div.style.fontWeight = 'bold';
            div.style.whiteSpace = 'nowrap';
            div.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)';
            div.style.border = '1px solid #000';
            div.textContent = displayCode || `Slot ${slot}`;

            const panes = this.getPanes();
            panes.floatPane.appendChild(div);
            this.div = div;

            marker.addListener('position_changed', () => {
                this.draw();
            });
        };

        overlay.draw = function() {
            const projection = this.getProjection();
            const markerPosition = marker.getPosition();
            const point = projection.fromLatLngToDivPixel(markerPosition);

            if (this.div && point) {
                this.div.style.left = (point.x - this.div.offsetWidth / 2) + 'px';
                this.div.style.top = (point.y + 25) + 'px';
            }
        };

        overlay.onRemove = function() {
            if (this.div) {
                this.div.parentNode.removeChild(this.div);
                this.div = null;
            }
        };

        overlay.setMap(map);
        marker.overlay = overlay;

        const infoWindow = new google.maps.InfoWindow({
            content: `
                <div style="padding: 8px;">
                    <strong>${displayCode ? 'Transect Code' : 'Location'}:</strong> ${code}<br>
                    <strong>Number:</strong> ${slot}<br>
                    <small class="text-muted">Drag marker to adjust location</small>
                </div>
            `,
        });

        marker.addListener('click', function() {
            infoWindow.open(map, marker);
        });

        marker.addListener('dragend', function(event) {
            const newLat = event.latLng.lat();
            const newLng = event.latLng.lng();

            if (latField) latField.value = newLat.toFixed(6);
            if (lngField) lngField.value = newLng.toFixed(6);
        });

        markers.push(marker);
        bounds.extend(position);
    });

    if (markers.length > 0) {
        map.fitBounds(bounds);
        if (markers.length === 1) {
            map.setZoom(18);
        }
    }

    updateTransectStatus(countEnteredTransectCodes());
}

function updateTransectStatus(codeCount) {
    const statusDiv = document.getElementById('transect-status');
    const countSpan = document.getElementById('transect-count');
    const mapBadge = document.getElementById('transect-map-badge');

    if (mapBadge) {
        if (markers.length > 0) {
            mapBadge.textContent = `${markers.length} on map`;
            mapBadge.classList.remove('hidden-field');
        } else {
            mapBadge.classList.add('hidden-field');
        }
    }

    if (!statusDiv || !countSpan) {
        return;
    }

    countSpan.textContent = codeCount;

    if (codeCount > 0 || markers.length > 0) {
        statusDiv.style.display = 'block';
        if (markers.length > 0) {
            statusDiv.className = 'alert alert-success mb-0';
            statusDiv.innerHTML = '<i class="fas fa-check-circle"></i> '
                + markers.length + ' marker(s) visible on the map — review positions before continuing';
        } else if (codeCount > 0) {
            statusDiv.className = 'alert alert-warning mb-0';
            statusDiv.innerHTML = '<i class="fas fa-info-circle"></i> '
                + codeCount + ' transect code(s) entered — add latitude and longitude to see markers';
        }
    } else {
        statusDiv.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    if (map) {
        setupTransectCodeMonitoring();
    }
});

bootstrapGoogleMapsFromContext();
