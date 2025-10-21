let map;
let markers = [];
let loadingCircle = null;
let loadingOverlay = null;

window.initMap = function() {
    console.log('initMap called - Google Maps API loaded');
    
    const jsonContextElement = document.getElementById('json_context');
    if (!jsonContextElement) {
        console.error('json_context element not found!');
        return;
    }
    
    let jsonContext;
    try {
        jsonContext = JSON.parse(jsonContextElement.textContent);
        console.log('Parsed JSON context:', jsonContext);
    } catch (e) {
        console.error('Error parsing JSON context:', e);
        console.error('JSON content:', jsonContextElement.textContent);
        return;
    }
    
    const transectData = jsonContext.transectData;
    const fieldCenter = { lat: jsonContext.fieldLatitude, lng: jsonContext.fieldLongitude };
    
    console.log('Transect data:', transectData);
    console.log('Field center:', fieldCenter);
    
    map = new google.maps.Map(document.getElementById("map"), {
        center: fieldCenter,
        zoom: 17,
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
    
    new google.maps.Marker({
        position: fieldCenter,
        map: map,
        title: "Field Center",
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 10,
            fillColor: "#4CAF50",
            fillOpacity: 1,
            strokeColor: "#2E7D32",
            strokeWeight: 2
        },
        label: {
            text: "FIELD",
            color: "white",
            fontSize: "10px",
            fontWeight: "bold"
        }
    });
    
    const locateButton = document.getElementById('locateMe');
    
    if (locateButton) {
        locateButton.addEventListener('click', function() {
            if (navigator.geolocation) {
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
                        const userLocation = {
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
        });
    }
    
    const markerColors = ['#FF5252', '#2196F3', '#FFC107', '#9C27B0'];
    const markerLabels = ['1', '2', '3', '4'];
    
    transectData.forEach((transect, index) => {
        const position = { lat: transect.latitude, lng: transect.longitude };
        
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
            
            const latInput = document.getElementById(`id_form-${transect.index}-transect_latitude`);
            const lngInput = document.getElementById(`id_form-${transect.index}-transect_longitude`);
            const coordsDisplay = document.getElementById(`coords_display_${transect.index}`);
            
            if (latInput) latInput.value = newLat.toFixed(6);
            if (lngInput) lngInput.value = newLng.toFixed(6);
            if (coordsDisplay) {
                coordsDisplay.textContent = `${newLat.toFixed(6)}, ${newLng.toFixed(6)}`;
                coordsDisplay.parentElement.parentElement.classList.add('alert-success');
                coordsDisplay.parentElement.parentElement.classList.remove('alert-light');
            }
            
            console.log(`Transect ${transect.code} moved to: ${newLat.toFixed(6)}, ${newLng.toFixed(6)}`);
        });
        
        markers.push(marker);
    });
    
    console.log(`Initialized map with ${transectData.length} transect markers`);
};

document.addEventListener('DOMContentLoaded', function() {
    const supportsDairyCheckboxes = document.querySelectorAll('.supports-dairy-checkbox');
    
    supportsDairyCheckboxes.forEach(function(checkbox) {
        const transectIndex = checkbox.getAttribute('data-transect');
        const confinedDiv = document.getElementById(`confined_dairy_${transectIndex}`);
        
        function toggleConfinedDairy() {
            if (confinedDiv) {
                confinedDiv.style.display = checkbox.checked ? 'block' : 'none';
            }
        }
        
        checkbox.addEventListener('change', toggleConfinedDairy);
        toggleConfinedDairy();
    });
});

