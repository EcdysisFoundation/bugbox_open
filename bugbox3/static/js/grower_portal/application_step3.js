import { bootstrapGoogleMapsFromContext } from './google_maps_api_loader';

let map;
let markers = [];
let userLocation = null;
let loadingCircle = null;
let loadingOverlay = null;

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
    
    let initialCenter = { lat: 37.7749, lng: -122.4194 }; // Default center (San Francisco)
    let initialZoom = 10;
    
    const transectData = jsonContext.transectData || [];
    if (transectData && transectData.length > 0) {
        const validTransects = transectData.filter(t => t.latitude && t.longitude);
        if (validTransects.length > 0) {
            const avgLat = validTransects.reduce((sum, t) => sum + t.latitude, 0) / validTransects.length;
            const avgLng = validTransects.reduce((sum, t) => sum + t.longitude, 0) / validTransects.length;
            initialCenter = { lat: avgLat, lng: avgLng };
            initialZoom = 17;
        }
    }
    
    map = new google.maps.Map(document.getElementById("map"), {
        center: initialCenter,
        zoom: initialZoom,
        mapTypeId: 'hybrid',
        mapTypeControl: true,
        mapTypeControlOptions: {
            style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR,
            position: google.maps.ControlPosition.TOP_RIGHT
        },
        zoomControl: true,
        streetViewControl: false,
        fullscreenControl: true
    });
    
    const locateButton = document.getElementById('locateMe');
    if (locateButton) {
        locateButton.addEventListener('click', handleLocateMe);
    }
    
    if (transectData && transectData.length > 0) {
        transectData.forEach((transect) => {
            const latField = document.getElementById(`id_transect_${transect.index + 1}_latitude`);
            const lngField = document.getElementById(`id_transect_${transect.index + 1}_longitude`);
            if (latField && lngField && transect.latitude && transect.longitude) {
                latField.value = transect.latitude;
                lngField.value = transect.longitude;
            }
        });
    }
    
    setupTransectCodeMonitoring();
    
};

function handleLocateMe() {
    if (navigator.geolocation) {
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
            radius: 50
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
                userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
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
                
                map.setCenter(userLocation);
                map.setZoom(18);
                updateTransectMarkers();        
                const locateButton = document.getElementById('locateMe');
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
                const locateButton = document.getElementById('locateMe');
                locateButton.innerHTML = '<i class="fas fa-crosshairs"></i> Locate Me';
                locateButton.disabled = false;
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    } else {
        alert('Geolocation is not supported by your browser.');
    }
}

function setupTransectCodeMonitoring() {
    const transectInputs = [
        'id_transect_code_1',
        'id_transect_code_2', 
        'id_transect_code_3',
        'id_transect_code_4'
    ];
    
    transectInputs.forEach((inputId, index) => {
        const element = document.getElementById(inputId);
        if (element) {
            element.addEventListener('input', () => updateTransectMarkers());
            element.addEventListener('change', () => updateTransectMarkers());
        }
    });
    
    updateTransectMarkers();
}

function updateTransectMarkers() {
    markers.forEach(marker => {
        marker.setMap(null);
        if (marker.overlay) {
            marker.overlay.setMap(null);
        }
    });
    markers = [];
    
    const markerColors = ['#FF5252', '#2196F3', '#FFC107', '#9C27B0'];
    const markerLabels = ['1', '2', '3', '4'];
    
    const transectCodes = [];
    for (let i = 1; i <= 4; i++) {
        const element = document.getElementById(`id_transect_code_${i}`);
        if (element && element.value.trim()) {
            const codeValue = element.value.trim();
            transectCodes.push({
                code: codeValue,
                index: i - 1
            });
        }
    }
    
    
    transectCodes.forEach((transect, index) => {
        const latField = document.getElementById(`id_transect_${index + 1}_latitude`);
        const lngField = document.getElementById(`id_transect_${index + 1}_longitude`);
        
        let position;
        if (latField && lngField && latField.value && lngField.value) {
            position = {
                lat: parseFloat(latField.value),
                lng: parseFloat(lngField.value)
            };
        } else if (userLocation) {
            const offset = 0.0001;
            position = {
                lat: userLocation.lat + (index * offset),
                lng: userLocation.lng + (index * offset)
            };
            
            if (latField) latField.value = position.lat.toFixed(6);
            if (lngField) lngField.value = position.lng.toFixed(6);
        } else {
            return;
        }
        
        const marker = new google.maps.Marker({
            position: position,
            map: map,
            title: `Transect ${transect.code}`,
            draggable: true,
            icon: {
                path: google.maps.SymbolPath.BACKWARD_CLOSED_ARROW,
                scale: 6,
                fillColor: markerColors[index % markerColors.length],
                fillOpacity: 1,
                strokeColor: "#000000",
                strokeWeight: 2
            },
            label: {
                text: markerLabels[index],
                color: "white",
                fontSize: "14px",
                fontWeight: "bold"
            }
        });
        
        const overlay = new google.maps.OverlayView();
        overlay.onAdd = function() {
            const div = document.createElement('div');
            div.style.position = 'absolute';
            div.style.backgroundColor = markerColors[index % markerColors.length];
            div.style.color = 'white';
            div.style.padding = '4px 8px';
            div.style.borderRadius = '4px';
            div.style.fontSize = '11px';
            div.style.fontWeight = 'bold';
            div.style.whiteSpace = 'nowrap';
            div.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)';
            div.style.border = '1px solid #000';
            div.textContent = transect.code;
            
            const panes = this.getPanes();
            panes.floatPane.appendChild(div);
            this.div = div;
            
            marker.addListener('position_changed', () => {
                this.draw();
            });
        };
        
        overlay.draw = function() {
            const projection = this.getProjection();
            const position = marker.getPosition();
            const point = projection.fromLatLngToDivPixel(position);
            
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
                    <strong>Transect Code:</strong> ${transect.code}<br>
                    <strong>Number:</strong> ${index + 1}<br>
                    <small class="text-muted">Drag marker to set location</small>
                </div>
            `
        });
        
        marker.addListener('click', function() {
            infoWindow.open(map, marker);
        });
        
        marker.addListener('dragend', function(event) {
            const newLat = event.latLng.lat();
            const newLng = event.latLng.lng();
            
            const latField = document.getElementById(`id_transect_${transect.index + 1}_latitude`);
            const lngField = document.getElementById(`id_transect_${transect.index + 1}_longitude`);
            
            if (latField) latField.value = newLat.toFixed(6);
            if (lngField) lngField.value = newLng.toFixed(6);
            
        });
        
        markers.push(marker);
    });
    
    
    updateTransectStatus(transectCodes.length);
}

function updateTransectStatus(count) {
    const statusDiv = document.getElementById('transect-status');
    const countSpan = document.getElementById('transect-count');
    const locateMessage = document.getElementById('locate-message');
    
    if (statusDiv && countSpan) {
        countSpan.textContent = count;
        
        if (count > 0) {
            statusDiv.style.display = 'block';
            if (markers.length > 0) {
                statusDiv.className = 'alert alert-success';
            } else {
                statusDiv.className = 'alert alert-warning';
                statusDiv.innerHTML = '<i class="fas fa-info-circle"></i> ' + count + ' transect(s) entered. Click "Locate Me" to display markers on the map.';
            }
        } else {
            statusDiv.style.display = 'none';
        }
    }
    if (locateMessage) {
        if (count > 0 && markers.length === 0 && !userLocation) {
            locateMessage.style.display = 'block';
        } else {
            locateMessage.style.display = 'none';
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    
    if (map) {
        setupTransectCodeMonitoring();
    }
});

bootstrapGoogleMapsFromContext();

