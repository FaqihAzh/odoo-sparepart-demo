/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, onMounted, useRef, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class CustomerMapDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.notification = useService("notification");
        this.mapRef = useRef("mapContainer");

        this.state = useState({
            loading: true,
            customerCount: 0,
        });

        // expose method for popup buttons
        window.customerMapDashboard = {
            openCustomerForm: (id) => this.openCustomerForm(id),
        };

        onMounted(async () => {
            await this.initializeMapDashboard();
        });
    }

    async initializeMapDashboard() {
        const mapContainer = this.mapRef.el;
        if (!mapContainer || !window.L) {
            console.error("Map container or Leaflet not found");
            this.state.loading = false;
            return;
        }

        try {
            // Initialize map centered on Jakarta
            this.map = window.L.map(mapContainer).setView([-6.2, 106.8], 11);

            // Add tile layer
            window.L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                maxZoom: 19,
                attribution: '© OpenStreetMap contributors'
            }).addTo(this.map);

            // Load and display customer data
            await this.loadCustomerData();

            this.state.loading = false;
        } catch (error) {
            console.error("Error initializing map dashboard:", error);
            this.state.loading = false;
            this.notification.add("Failed to load map dashboard", { type: "danger" });
        }
    }

    async loadCustomerData() {
        try {
            // Fetch customer records with location data
            const records = await this.orm.searchRead(
                "customer.map",
                [['latitude', '!=', false], ['longitude', '!=', false]], // Only records with coordinates
                ["id", "name", "description", "phone", "email", "latitude", "longitude"]
            );

            console.log("Loaded customer records:", records);

            this.state.customerCount = records.length;

            // Create marker cluster group for better performance
            const markers = window.L.markerClusterGroup ? window.L.markerClusterGroup() : window.L.layerGroup();

            // Add markers for each customer
            records.forEach((record) => {
                this.addCustomerMarker(record, markers);
            });

            // Add marker group to map
            this.map.addLayer(markers);

            // Fit map bounds to show all markers
            if (records.length > 0) {
                const group = new window.L.featureGroup(markers.getLayers());
                this.map.fitBounds(group.getBounds().pad(0.1));
            }

            // Show notification
            if (records.length > 0) {
                this.notification.add(
                    `Loaded ${records.length} customer location${records.length > 1 ? 's' : ''}`,
                    { type: "success" }
                );
            } else {
                this.notification.add("No customer locations found", { type: "info" });
            }

        } catch (error) {
            console.error("Error loading customer data:", error);
            this.notification.add("Failed to load customer data", { type: "danger" });
        }
    }

    addCustomerMarker(record, markersGroup) {
        if (!record.latitude || !record.longitude) {
            return;
        }

        // Create custom icon (optional)
        const customIcon = window.L.divIcon({
            className: 'custom-customer-marker',
            html: `<div class="marker-content">
                     <i class="fa fa-user" style="color: #1f77b4; font-size: 16px;"></i>
                   </div>`,
            iconSize: [30, 30],
            iconAnchor: [15, 15]
        });

        // Create marker
        const marker = window.L.marker([record.latitude, record.longitude], {
            icon: customIcon
        });

        // Create popup content
        const popupContent = `
            <div class="customer-popup">
                <h4 style="margin: 0 0 10px 0; color: #1f77b4;">
                    <i class="fa fa-user"></i> ${record.name}
                </h4>
                ${record.description ? `<p><strong>Description:</strong> ${record.description}</p>` : ''}
                ${record.phone ? `<p><strong>Phone:</strong> ${record.phone}</p>` : ''}
                ${record.email ? `<p><strong>Email:</strong> ${record.email}</p>` : ''}
                <p><strong>Location:</strong> ${record.latitude.toFixed(6)}, ${record.longitude.toFixed(6)}</p>
                <div style="margin-top: 10px;">
                    <button onclick="window.customerMapDashboard.openCustomerForm(${record.id})"
                            class="btn btn-primary btn-sm">
                        <i class="fa fa-edit"></i> Edit
                    </button>
                </div>
            </div>
        `;

        marker.bindPopup(popupContent, {
            maxWidth: 300,
            className: 'customer-popup-container'
        });

        // Add click handler
        marker.on('click', () => {
            // Optional: You can add additional click behavior here
            console.log("Clicked customer:", record.name);
        });

        markersGroup.addLayer(marker);
    }

    async openCustomerForm(customerId) {
        try {
            await this.action.doAction({
                name: "Customer Details",
                type: "ir.actions.act_window",
                res_model: "customer.map",
                res_id: customerId,
                view_mode: "form",
                view_type: "form",
                views: [[false, "form"]],
                target: "current",
            });
        } catch (error) {
            console.error("Error opening customer form:", error);
            this.notification.add("Failed to open customer form", { type: "danger" });
        }
    }

    async refreshData() {
        this.state.loading = true;

        // Clear existing markers
        this.map.eachLayer((layer) => {
            if (layer instanceof window.L.MarkerClusterGroup || layer instanceof window.L.LayerGroup) {
                this.map.removeLayer(layer);
            }
        });

        // Reload data
        await this.loadCustomerData();
        this.state.loading = false;

        this.notification.add("Data refreshed", { type: "success" });
    }

    async addNewCustomer() {
        try {
            await this.action.doAction({
                name: "New Customer",
                type: "ir.actions.act_window",
                res_model: "customer.map",
                view_mode: "form",
                view_type: "form",
                views: [[false, "form"]],
                target: "current",
            });
        } catch (error) {
            console.error("Error creating new customer:", error);
            this.notification.add("Failed to create new customer", { type: "danger" });
        }
    }
}

CustomerMapDashboard.template = "customer_map_tracking.CustomerMapDashboard";

// Register the action
registry.category("actions").add("customer_map_tracking.map_dashboard", CustomerMapDashboard);