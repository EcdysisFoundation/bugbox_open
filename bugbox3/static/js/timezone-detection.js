(function() {
    'use strict';
    
    function detectTimezone() {
        try {
            const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            return timezone;
        } catch (e) {
            console.warn('Timezone detection failed, using UTC:', e);
            return 'UTC';
        }
    }
    
    function sendTimezoneToServer(timezone) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.style.display = 'none';
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = 'csrfmiddlewaretoken';
            csrfInput.value = csrfToken.value;
            form.appendChild(csrfInput);
        }
        
        const timezoneInput = document.createElement('input');
        timezoneInput.type = 'hidden';
        timezoneInput.name = 'timezone';
        timezoneInput.value = timezone;
        form.appendChild(timezoneInput);
        
        document.body.appendChild(form);
        form.submit();
    }
    
    function isTimezoneStored() {
        return document.querySelector('[data-user-timezone]') !== null;
    }
    
    function initTimezoneDetection() {
        if (isTimezoneStored()) {
            return;
        }
        
        const detectedTimezone = detectTimezone();
        console.log('Detected timezone:', detectedTimezone);
        
        sendTimezoneToServer(detectedTimezone);
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTimezoneDetection);
    } else {
        initTimezoneDetection();
    }
    
    window.addEventListener('load', initTimezoneDetection);
    
})();
