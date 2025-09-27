/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class CustomerMapDashboard extends Component {
    setup() {
        this.orm = useService("orm");

        onMounted(async () => {
            const container = this.el.querySelector("#customer_map");
            if (!container) return;

            // Init map
            const map = L.map(container).setView([-6.2, 106.8], 11);

            L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                maxZoom: 19,
            }).addTo(map);

            // Ambil data dari model
            const records = await this.orm.searchRead("customer.map", [], [
                "name",
                "latitude",
                "longitude",
            ]);

            records.forEach((rec) => {
                if (rec.latitude && rec.longitude) {
                    L.marker([rec.latitude, rec.longitude])
                        .addTo(map)
                        .bindPopup(`<b>${rec.name}</b><br/>Lat: ${rec.latitude}, Lon: ${rec.longitude}`);
                }
            });
        });
    }
}

CustomerMapDashboard.template = "customer_map_tracking.CustomerMapDashboard";

// Daftarkan ke action registry
registry.category("actions").add("customer_map_tracking.map_dashboard", CustomerMapDashboard);
