/** @odoo-module **/

/*  NO OWL IMPORT  – pakai global lama */
import ajax from "web.ajax";
import Dialog from "web.Dialog";

/* ---------- Dashboard Map (menu action) ---------- */
function initDashboardMap() {
    const el = document.getElementById('customer-map-dashboard');
    if (!el) return;              // bukan halaman dashboard
    el.innerHTML = '';
    const map = L.map(el).setView([-6.20, 106.82], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    ajax.jsonRpc('/customer_map_tracking/data', 'call', {}).then(function (data) {
        if (!data || !data.length) return;

        // auto-center ke rata-rata koordinat
        const avgLat = data.reduce((a, p) => a + p.latitude, 0) / data.length;
        const avgLng = data.reduce((a, p) => a + p.longitude, 0) / data.length;
        map.setView([avgLat, avgLng], 6);

        data.forEach(function (p) {
            const marker = L.marker([p.latitude, p.longitude]).addTo(map);
            marker.bindTooltip(p.name);
            marker.on('click', function () {
                ajax.jsonRpc('/customer_map_tracking/get/' + p.id, 'call', {}).then(function (detail) {
                    const content = `
                        <div class="o_map_popup">
                            <h4>${detail.name || ''}</h4>
                            <p>${detail.description || ''}</p>
                            <p><b>Email:</b> ${detail.email || '-'}</p>
                            <p><b>Phone:</b> ${detail.phone || '-'}</p>
                            <p><b>Lat:</b> ${detail.latitude || '-'} <b>Lng:</b> ${detail.longitude || '-'}</p>
                        </div>`;
                    new Dialog(null, {
                        title: detail.name || 'Detail',
                        $content: $(content),
                        size: 'medium',
                    }).open();
                });
            });
        });
    });
}

/* ---------- Form “Pick on map” button ---------- */
function initFormMapPicker() {
    const latInput = document.querySelector('input[name="latitude"], input[data-fieldname="latitude"]');
    if (!latInput || document.getElementById('open-map-picker-btn')) return;

    const btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'open-map-picker-btn';
    btn.className = 'btn btn-secondary btn-sm ms-1';
    btn.innerText = '🗺 Pick on map';
    latInput.parentNode.appendChild(btn);

    btn.addEventListener('click', function () {
        const mapDiv = document.createElement('div');
        mapDiv.id = 'customer-map-picker';
        mapDiv.style = 'height:500px; width:100%;';

        const dialog = new Dialog(null, {
            title: 'Pick location on map',
            $content: $(mapDiv),
            size: 'large',
        });
        dialog.open();

        setTimeout(function () {
            const picker = L.map('customer-map-picker').setView([-6.20, 106.82], 5);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; OpenStreetMap contributors'
            }).addTo(picker);

            let tempMarker;
            picker.on('click', function (e) {
                const { lat, lng } = e.latlng;
                tempMarker ? tempMarker.setLatLng(e.latlng)
                           : tempMarker = L.marker(e.latlng).addTo(picker);

                const lngField = document.querySelector('input[name="longitude"], input[data-fieldname="longitude"]');
                latInput.value  = lat.toFixed(6);
                lngField.value  = lng.toFixed(6);
                latInput.dispatchEvent(new Event('change', { bubbles: true }));
                lngField.dispatchEvent(new Event('change', { bubbles: true }));
            });
            picker.invalidateSize();
        }, 50);
    });
}

/* ---------- Jalankan ---------- */
document.addEventListener('DOMContentLoaded', function () {
    initDashboardMap();
    initFormMapPicker();
});