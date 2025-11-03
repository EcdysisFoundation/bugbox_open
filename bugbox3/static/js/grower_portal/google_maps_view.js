window.initMapView = function() {
    
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
    
    const transectData = jsonContext.transectData;
    const fieldCenter = { lat: jsonContext.fieldLatitude, lng: jsonContext.fieldLongitude };
    
    
    const map = new google.maps.Map(document.getElementById("map"), {
        center: fieldCenter,
        zoom: 16,
        mapTypeId: 'hybrid',
        mapTypeControl: true,
        zoomControl: true,
        streetViewControl: false,
        fullscreenControl: true
    });
    
    
    const markerColors = ['#FF5252', '#2196F3', '#FFC107', '#9C27B0'];
    const markerLabels = ['1', '2', '3', '4'];
    
    transectData.forEach((transect, index) => {
        const position = { lat: transect.latitude, lng: transect.longitude };
        
        const marker = new google.maps.Marker({
            position: position,
            map: map,
            title: `Transect ${transect.code}`,
            draggable: false,
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
        
        const infoWindow = new google.maps.InfoWindow({
            content: `
                <div style="padding: 8px;">
                    <strong>Transect Code:</strong> ${transect.code}<br>
                    <strong>Number:</strong> ${index + 1}<br>
                    <strong>Coordinates:</strong> ${transect.latitude.toFixed(6)}, ${transect.longitude.toFixed(6)}
                </div>
            `
        });
        
        marker.addListener('click', function() {
            infoWindow.open(map, marker);
        });
    });
    
};

