import { bootstrapGoogleMapsFromContext } from './google_maps_api_loader';

const MAX_TRANSECT_SLOTS = 4;
const MARKER_COLORS = ['#FF5252', '#2196F3', '#FFC107', '#9C27B0'];

let map;
let markers = [];
let loadingCircle = null;
let loadingOverlay = null;
let activeTransectSlot = 1;
let mapClickListener = null;
let visibleTransectSlotCount = 1;
const expandedEmptySlots = new Set();
let addTransectButtonInitialized = false;

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

function slotHasAnyData(slot) {
    const codeEl = document.getElementById(`id_transect_code_${slot}`);
    const latField = document.getElementById(`id_transect_${slot}_latitude`);
    const lngField = document.getElementById(`id_transect_${slot}_longitude`);
    const hasCode = Boolean(codeEl && codeEl.value.trim());
    const hasLat = latField && parseCoordinate(latField.value) !== null;
    const hasLng = lngField && parseCoordinate(lngField.value) !== null;
    return hasCode || hasLat || hasLng;
}

function getLastActiveTransectSlot() {
    let lastSlot = 0;
    for (let slot = 1; slot <= MAX_TRANSECT_SLOTS; slot++) {
        if (slotHasAnyData(slot)) {
            lastSlot = slot;
        }
    }
    return lastSlot || 1;
}

function recalculateVisibleTransectSlots() {
    const lastActive = getLastActiveTransectSlot();
    let visible = Math.max(1, lastActive);

    expandedEmptySlots.forEach((slot) => {
        visible = Math.max(visible, slot);
    });

    visibleTransectSlotCount = Math.min(MAX_TRANSECT_SLOTS, visible);

    expandedEmptySlots.forEach((slot) => {
        if (slot > visibleTransectSlotCount) {
            expandedEmptySlots.delete(slot);
        }
    });
}

function syncExpandedEmptySlots() {
    for (let slot = 1; slot <= MAX_TRANSECT_SLOTS; slot++) {
        if (slotHasAnyData(slot)) {
            expandedEmptySlots.delete(slot);
        }
    }
}

function updateTransectRowVisibility() {
    syncExpandedEmptySlots();
    recalculateVisibleTransectSlots();
    applyTransectRowVisibility();
}

function updateAddTransectButton() {
    const button = document.getElementById('add-transect-location');
    if (!button) {
        return;
    }

    const canAddMore = visibleTransectSlotCount < MAX_TRANSECT_SLOTS;
    button.classList.toggle('hidden-field', !canAddMore);
}

function updateMapSlotSelectorVisibility() {
    for (let slot = 1; slot <= MAX_TRANSECT_SLOTS; slot++) {
        const isVisible = slot <= visibleTransectSlotCount;
        const selectorButton = document.querySelector(
            `[data-active-transect-slot="${slot}"]`,
        );
        if (selectorButton) {
            selectorButton.classList.toggle('hidden-field', !isVisible);
        }

        const selectOption = document.querySelector(
            `#active-transect-slot option[value="${slot}"]`,
        );
        if (selectOption) {
            selectOption.hidden = !isVisible;
            selectOption.disabled = !isVisible;
        }
    }
}

function setupAddTransectButton() {
    if (addTransectButtonInitialized) {
        return;
    }

    const button = document.getElementById('add-transect-location');
    if (!button) {
        return;
    }

    addTransectButtonInitialized = true;
    button.addEventListener('click', () => {
        if (visibleTransectSlotCount >= MAX_TRANSECT_SLOTS) {
            return;
        }

        const nextSlot = visibleTransectSlotCount + 1;
        expandedEmptySlots.add(nextSlot);
        visibleTransectSlotCount = nextSlot;
        applyTransectRowVisibility();
        setActiveTransectSlot(nextSlot);

        const codeField = document.getElementById(`id_transect_code_${nextSlot}`);
        if (codeField) {
            codeField.focus();
        }
    });
}

function applyTransectRowVisibility() {
    for (let slot = 1; slot <= MAX_TRANSECT_SLOTS; slot++) {
        setRowVisible(slot, slot <= visibleTransectSlotCount);
    }

    updateAddTransectButton();
    updateMapSlotSelectorVisibility();

    if (activeTransectSlot > visibleTransectSlotCount) {
        setActiveTransectSlot(visibleTransectSlotCount);
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

    visibleTransectSlotCount = getLastActiveTransectSlot();
    setupTransectPlacementControls();
    updateTransectRowVisibility();
    updateTransectMarkers({ fitBounds: true });
};

function setupTransectFormControls() {
    visibleTransectSlotCount = getLastActiveTransectSlot();
    setupAddTransectButton();
    setupTransectCodeMonitoring();
}

function setActiveTransectSlot(slot) {
    const parsedSlot = parseInt(slot, 10);
    if (!Number.isFinite(parsedSlot) || parsedSlot < 1 || parsedSlot > MAX_TRANSECT_SLOTS) {
        return;
    }

    activeTransectSlot = parsedSlot;

    document.querySelectorAll('[data-active-transect-slot]').forEach((button) => {
        const buttonSlot = parseInt(button.dataset.activeTransectSlot, 10);
        const isActive = buttonSlot === activeTransectSlot;
        button.classList.toggle('active', isActive);
        button.setAttribute('aria-pressed', isActive ? 'true' : 'false');
    });

    const select = document.getElementById('active-transect-slot');
    if (select) {
        select.value = String(activeTransectSlot);
    }

    document.querySelectorAll('.transect-location-row[data-slot]').forEach((row) => {
        const rowSlot = parseInt(row.dataset.slot, 10);
        row.classList.toggle('transect-location-card--active', rowSlot === activeTransectSlot);
    });

    const mapEl = document.getElementById('map');
    if (mapEl) {
        mapEl.classList.add('map-container--placing');
    }
}

function setupTransectPlacementControls() {
    document.querySelectorAll('[data-active-transect-slot]').forEach((button) => {
        button.addEventListener('click', () => {
            setActiveTransectSlot(button.dataset.activeTransectSlot);
        });
    });

    const select = document.getElementById('active-transect-slot');
    if (select) {
        select.addEventListener('change', () => {
            setActiveTransectSlot(select.value);
        });
    }

    for (let slot = 1; slot <= MAX_TRANSECT_SLOTS; slot++) {
        const row = document.querySelector(`.transect-location-row[data-slot="${slot}"]`);
        if (!row) {
            continue;
        }

        row.addEventListener('click', (event) => {
            if (event.target.closest('input, select, textarea, button, a, label')) {
                return;
            }
            setActiveTransectSlot(slot);
        });

        const fieldIds = [
            `id_transect_code_${slot}`,
            `id_transect_${slot}_latitude`,
            `id_transect_${slot}_longitude`,
        ];
        fieldIds.forEach((inputId) => {
            const element = document.getElementById(inputId);
            if (element) {
                element.addEventListener('focus', () => setActiveTransectSlot(slot));
            }
        });
    }

    if (mapClickListener) {
        google.maps.event.removeListener(mapClickListener);
    }
    mapClickListener = map.addListener('click', handleMapClickPlaceTransect);

    setActiveTransectSlot(activeTransectSlot);
}

function handleMapClickPlaceTransect(event) {
    const lat = event.latLng.lat();
    const lng = event.latLng.lng();
    const latField = document.getElementById(`id_transect_${activeTransectSlot}_latitude`);
    const lngField = document.getElementById(`id_transect_${activeTransectSlot}_longitude`);

    if (!latField || !lngField) {
        return;
    }

    latField.value = lat.toFixed(6);
    lngField.value = lng.toFixed(6);
    latField.dispatchEvent(new Event('input', { bubbles: true }));
    lngField.dispatchEvent(new Event('change', { bubbles: true }));

    updateTransectRowVisibility();
    updateTransectMarkers({ fitBounds: false });
    highlightPlacedTransect(activeTransectSlot);
}

function highlightPlacedTransect(slot) {
    const row = document.querySelector(`.transect-location-row[data-slot="${slot}"]`);
    if (!row) {
        return;
    }

    row.classList.add('transect-location-card--placed');
    window.setTimeout(() => {
        row.classList.remove('transect-location-card--placed');
    }, 1200);
}

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
    visibleTransectSlotCount = getLastActiveTransectSlot();

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
    updateTransectMarkers({ fitBounds: true });
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

function updateTransectMarkers(options = {}) {
    const fitBounds = options.fitBounds !== false;

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
        const colorIndex = (slot - 1) % MARKER_COLORS.length;

        const marker = new google.maps.Marker({
            position: position,
            map: map,
            title: `Transect ${code}`,
            draggable: true,
            icon: {
                path: google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
                scale: 6,
                fillColor: MARKER_COLORS[colorIndex],
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
            div.style.backgroundColor = MARKER_COLORS[colorIndex];
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
            setActiveTransectSlot(slot);
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

    if (fitBounds && markers.length > 0) {
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
                + markers.length + ' marker(s) visible on the map, review positions before continuing';
        } else if (codeCount > 0) {
            statusDiv.className = 'alert alert-warning mb-0';
            statusDiv.innerHTML = '<i class="fas fa-info-circle"></i> '
                + codeCount + ' transect code(s) entered, add latitude and longitude to see markers';
        }
    } else {
        statusDiv.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    setupTransectFormControls();
});

bootstrapGoogleMapsFromContext();
