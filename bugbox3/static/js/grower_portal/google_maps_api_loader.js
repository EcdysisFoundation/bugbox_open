export function bootstrapGoogleMapsFromContext() {
    const el = document.getElementById('json_context');
    if (!el) {
        return;
    }

    let ctx;
    try {
        ctx = JSON.parse(el.textContent);
    } catch (e) {
        console.error('Error parsing json_context for Google Maps:', e);
        return;
    }

    const apiKey = ctx.googleMapsApiKey;
    const callback = ctx.googleMapsCallback;
    const version = ctx.googleMapsVersion || 'weekly';
    if (!apiKey || !callback) {
        return;
    }

    if (window.google && window.google.maps) {
        const fn = window[callback];
        if (typeof fn === 'function') {
            fn();
        }
        return;
    }

    if (document.querySelector('script[data-grower-google-maps]')) {
        return;
    }

    const script = document.createElement('script');
    script.dataset.growerGoogleMaps = '1';
    script.src = (
        'https://maps.googleapis.com/maps/api/js'
        + `?key=${encodeURIComponent(apiKey)}`
        + `&callback=${encodeURIComponent(callback)}`
        + `&v=${encodeURIComponent(version)}`
    );
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
}
