/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted } from "@odoo/owl";

export class MapPickerField extends Component {
    setup() {
        onMounted(() => {
            const mapContainer = this.el.querySelector("#map_picker");
            if (!mapContainer) return;

            const map = L.map(mapContainer).setView([-6.2, 106.8], 10);

            L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                maxZoom: 19,
            }).addTo(map);

            let marker;
            map.on("click", (e) => {
                if (marker) {
                    marker.setLatLng(e.latlng);
                } else {
                    marker = L.marker(e.latlng).addTo(map);
                }
                // Isi nilai ke field Odoo
                this.props.update(e.latlng.lat, e.latlng.lng);
            });
        });
    }
}

MapPickerField.template = "customer_map_tracking.MapPickerField";

// Daftarkan ke field registry
registry.category("fields").add("map_picker", MapPickerField);
