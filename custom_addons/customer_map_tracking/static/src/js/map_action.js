odoo.define('customer_map_tracking.MapAction', function (require) {
    "use strict";

    var core = require('web.core');
    var AbstractAction = require('web.AbstractAction');
    var rpc = require('web.rpc');
    var _t = core._t;
    var QWeb = core.qweb;
    var session = require('web.session');

    var MapAction = AbstractAction.extend({
        template: 'CustomerMapTracking.MapView',
        init: function(parent, action) {
            this._super(parent, action);
            this.records = [];
            // context: action.context may contain map_picker and active_id
            this.map_picker = (action && action.context && action.context.map_picker) || false;
            this.active_id = (action && action.context && action.context.active_id) || false;
            this.map = false;
            this.markerLayer = false;
        },
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                // after template rendered
                self.$map = self.$el.find('#customer_map');
                self.$refresh = self.$el.find('.o-refresh-markers');
                self.$refresh.on('click', function(){ self.loadMarkers(); });
                return self.loadMarkers();
            });
        },
        loadMarkers: function(){
            var self = this;
            return rpc.query({
                model: 'customer.worker',
                method: 'search_read',
                args: [[], ['id','name','description','lat','lon','image']]
            }).then(function(records){
                self.records = records || [];
                self.renderMap();
            });
        },
        renderMap: function(){
            var self = this;
            if (!this.$map.length) { return; }

            // default center (if no points)
            var defaultLat = -6.200000;
            var defaultLon = 106.816666;
            var startLat = defaultLat;
            var startLon = defaultLon;
            if (this.records.length && this.records[0].lat && this.records[0].lon){
                startLat = this.records[0].lat;
                startLon = this.records[0].lon;
            }

            // destroy old map if present
            if (this.map) {
                try { this.map.remove(); } catch (e) {}
                this.map = null;
            }

            // create map
            this.map = L.map(this.$map.get(0)).setView([startLat, startLon], 6);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '© OpenStreetMap contributors'
            }).addTo(this.map);

            // marker layer
            this.markerLayer = L.layerGroup().addTo(this.map);

            // add markers
            this.records.forEach(function(rec){
                if (rec.lat && rec.lon){
                    var marker = L.marker([rec.lat, rec.lon]).addTo(self.markerLayer);
                    var content = "<div style='min-width:180px;'>";
                    content += "<b>" + _.escape(rec.name) + "</b><br/>";
                    content += (rec.description ? _.escape(rec.description).substring(0,200) + "<br/>" : "");
                    content += "<div style='margin-top:6px;'>";
                    content += "<button class='btn btn-sm btn-primary open-record' data-id='" + rec.id + "'>Open</button> ";
                    content += "</div></div>";
                    marker.bindPopup(content);
                }
            });

            // click handler for the popup Open button
            this.$el.off('click', '.open-record').on('click', '.open-record', function(ev){
                var id = $(this).data('id');
                if (!id) { return; }
                // open record form
                self.do_action({
                    type: 'ir.actions.act_window',
                    res_model: 'customer.worker',
                    res_id: id,
                    views: [[false, 'form']],
                });
            });

            // If map picker mode is active (opened from form "Pick on Map"), allow click to set lat/lon
            if (this.map_picker && this.active_id) {
                var pickerMsg = L.popup().setLatLng(this.map.getCenter()).setContent("Click on map to pick location").openOn(this.map);
                this.map.on('click', function(e){
                    var lat = e.latlng.lat;
                    var lon = e.latlng.lng;
                    // write lat/lon to the active record
                    rpc.query({
                        model: 'customer.worker',
                        method: 'write',
                        args: [[self.active_id], {lat: lat, lon: lon}]
                    }).then(function(res){
                        // close the client action (dialog)
                        try {
                            self.do_notify(_t("Location saved"), _t("Lat: ") + lat.toFixed(6) + ", " + _t("Lon: ") + lon.toFixed(6));
                        } catch (err) {
                            // fallback
                            console.log("Saved location", lat, lon);
                        }
                        // close (if opened as dialog)
                        try { self.do_action({type: 'ir.actions.act_window_close'}); } catch (e) { window.history.back(); }
                    });
                });
            }

            // fit bounds to markers if any
            var coords = this.records.filter(function(r){ return r.lat && r.lon; }).map(function(r){ return [r.lat, r.lon]; });
            if (coords.length > 0){
                var bounds = L.latLngBounds(coords);
                this.map.fitBounds(bounds.pad(0.2));
            }
        },
    });

    core.action_registry.add('customer_map_tracking.map_action', MapAction);
});
