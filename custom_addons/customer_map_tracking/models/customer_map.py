# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class CustomerMap(models.Model):
    _name = 'customer.map'
    _description = 'Customer / Worker with Map Tracking'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Name', required=True, tracking=True)
    description = fields.Text(string='Description', tracking=True)
    phone = fields.Char(string='Phone', tracking=True)
    email = fields.Char(string='Email', tracking=True)

    # PostGIS Geometry field - this is the main field like in Field Service
    shape = fields.GeoPoint(
        string='Location',
        help='Location coordinates using PostGIS geometry'
    )

    # Backup coordinate fields for compatibility and manual entry
    latitude = fields.Float(
        string='Latitude',
        digits=(16, 6),
        tracking=True,
        help='Latitude coordinate (manual entry)'
    )
    longitude = fields.Float(
        string='Longitude',
        digits=(16, 6),
        tracking=True,
        help='Longitude coordinate (manual entry)'
    )

    # Computed field for display
    location_display = fields.Char(
        string='Location',
        compute='_compute_location_display',
        store=True
    )

    # WKT geometry field for display/export
    geo_wkt = fields.Char(
        string='Geometry (WKT)',
        compute='_compute_geo_wkt',
        store=True
    )

    # Status field
    active = fields.Boolean(default=True, tracking=True)

    @api.depends('shape', 'latitude', 'longitude')
    def _compute_location_display(self):
        """Compute human-readable location display"""
        for rec in self:
            if rec.shape:
                # Get coordinates from PostGIS geometry
                try:
                    geom = rec.shape
                    if hasattr(geom, 'coords') and geom.coords:
                        lon, lat = geom.coords[0], geom.coords[1]
                        rec.location_display = f"Lat: {lat:.6f}, Lng: {lon:.6f}"
                    else:
                        rec.location_display = "PostGIS Geometry Set"
                except:
                    rec.location_display = "PostGIS Geometry Set"
            elif rec.latitude is not None and rec.longitude is not None:
                rec.location_display = f"Lat: {rec.latitude:.6f}, Lng: {rec.longitude:.6f}"
            else:
                rec.location_display = "No location set"

    @api.depends('shape', 'latitude', 'longitude')
    def _compute_geo_wkt(self):
        """Compute WKT geometry for display"""
        for rec in self:
            if rec.shape:
                try:
                    # Get WKT from PostGIS geometry
                    if hasattr(rec.shape, 'wkt'):
                        rec.geo_wkt = rec.shape.wkt
                    else:
                        rec.geo_wkt = str(rec.shape)
                except:
                    rec.geo_wkt = "PostGIS Geometry"
            elif rec.latitude is not None and rec.longitude is not None:
                rec.geo_wkt = f'POINT({rec.longitude} {rec.latitude})'
            else:
                rec.geo_wkt = False

    @api.constrains('latitude', 'longitude')
    def _check_coordinates(self):
        """Validate coordinate ranges"""
        for rec in self:
            if rec.latitude is not None and (rec.latitude < -90 or rec.latitude > 90):
                raise ValidationError(_('Latitude must be between -90 and 90 degrees.'))
            if rec.longitude is not None and (rec.longitude < -180 or rec.longitude > 180):
                raise ValidationError(_('Longitude must be between -180 and 180 degrees.'))

    @api.constrains('email')
    def _check_email(self):
        """Validate email format"""
        for rec in self:
            if rec.email and '@' not in rec.email:
                raise ValidationError(_('Please enter a valid email address.'))

    def set_location_from_coordinates(self, lat, lng):
        """Set PostGIS geometry from latitude/longitude coordinates"""
        self.ensure_one()

        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            raise ValidationError(
                _('Invalid coordinates. Latitude must be between -90 and 90, longitude between -180 and 180.'))

        # Create PostGIS POINT geometry
        from shapely.geometry import Point
        try:
            point = Point(lng, lat)  # Note: PostGIS uses (longitude, latitude)
            self.write({
                'shape': point,
                'latitude': lat,
                'longitude': lng
            })
        except ImportError:
            # Fallback if shapely is not available
            self.write({
                'latitude': lat,
                'longitude': lng
            })
            # Use raw SQL to create PostGIS geometry
            self._cr.execute("""
                UPDATE customer_map 
                SET shape = ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                WHERE id = %s
            """, (lng, lat, self.id))

        return True

    @api.model
    def create(self, vals):
        """Override create to sync coordinates with PostGIS geometry"""
        result = super().create(vals)

        # Sync coordinates to PostGIS if provided
        if vals.get('latitude') and vals.get('longitude') and not vals.get('shape'):
            result.set_location_from_coordinates(vals['latitude'], vals['longitude'])

        # Log creation
        if result.shape or (vals.get('latitude') and vals.get('longitude')):
            result.message_post(
                body=_('Customer location created: %s') % result.location_display,
                message_type='notification'
            )

        return result

    def write(self, vals):
        """Override write to sync coordinates with PostGIS geometry"""
        # Store old locations for tracking
        old_locations = {}
        if any(field in vals for field in ['latitude', 'longitude', 'shape']):
            for rec in self:
                old_locations[rec.id] = rec.location_display

        result = super().write(vals)

        # Sync coordinates to PostGIS if provided
        if 'latitude' in vals and 'longitude' in vals and vals['latitude'] and vals['longitude']:
            for rec in self:
                if not vals.get('shape'):  # Only sync if shape wasn't explicitly set
                    rec.set_location_from_coordinates(vals['latitude'], vals['longitude'])

        # Log location changes
        if any(field in vals for field in ['latitude', 'longitude', 'shape']):
            for rec in self:
                if rec.id in old_locations:
                    old_loc = old_locations[rec.id]
                    new_loc = rec.location_display
                    if old_loc != new_loc:
                        rec.message_post(
                            body=_('Location changed from "%s" to "%s"') % (old_loc, new_loc),
                            message_type='notification'
                        )

        return result

    def action_clear_location(self):
        """Clear all location data"""
        self.write({
            'shape': False,
            'latitude': False,
            'longitude': False
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Location Cleared'),
                'message': _('Location coordinates have been cleared.'),
                'type': 'success',
            }
        }

    def action_geocode_address(self):
        """Geocode address - placeholder for geocoding service integration"""
        # This would integrate with geocoding services like Google Maps, Nominatim, etc.
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Geocoding'),
                'message': _('Geocoding service not configured. Please set location manually.'),
                'type': 'info',
            }
        }

    def action_open_map_view(self):
        """Open this customer in map view"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Customer Location Map'),
            'res_model': 'customer.map',
            'view_mode': 'geoengine',
            'domain': [('id', '=', self.id)],
            'context': {'create': False, 'edit': False},
        }

    @api.model
    def get_customers_geojson(self):
        """Get customer data in GeoJSON format for external integrations"""
        customers = self.search([
            ('shape', '!=', False),
            ('active', '=', True)
        ])

        features = []
        for customer in customers:
            try:
                if customer.shape:
                    # Extract coordinates from PostGIS geometry
                    feature = {
                        'type': 'Feature',
                        'properties': {
                            'id': customer.id,
                            'name': customer.name,
                            'description': customer.description or '',
                            'phone': customer.phone or '',
                            'email': customer.email or '',
                        },
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [customer.shape.coords[0], customer.shape.coords[1]]
                        }
                    }
                    features.append(feature)
            except Exception as e:
                _logger.warning("Failed to process geometry for customer %s: %s", customer.name, e)

        return {
            'type': 'FeatureCollection',
            'features': features
        }

    def name_get(self):
        """Custom name display"""
        result = []
        for rec in self:
            name = rec.name
            if rec.phone:
                name += f' ({rec.phone})'
            result.append((rec.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        """Enhanced name search including phone and email"""
        args = args or []
        if name:
            # Search in name, phone, and email
            domain = [
                '|', '|',
                ('name', operator, name),
                ('phone', operator, name),
                ('email', operator, name)
            ]
            customer_ids = self._search(domain + args, limit=limit, access_rights_uid=name_get_uid)
            return self.browse(customer_ids).name_get()
        return super()._name_search(name, args, operator, limit, name_get_uid)