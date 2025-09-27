# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class CustomerMap(models.Model):
    _name = 'customer.map'
    _description = 'Customer / Worker with Map Tracking'

    name = fields.Char(string='Name', required=True)
    description = fields.Text(string='Description')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')

    latitude = fields.Float(string='Latitude', digits=(16, 6))
    longitude = fields.Float(string='Longitude', digits=(16, 6))

    # interoperable geometry: store WKT POINT(lon lat) to integrate with other systems
    geo_wkt = fields.Char(string='Geometry (WKT)', compute='_compute_geo_wkt', store=True)

    # Optional: if you want a database geometry column for PostGIS, create it manually in DB
    # and use sync_to_postgis() to populate.

    @api.depends('latitude', 'longitude')
    def _compute_geo_wkt(self):
        for rec in self:
            if rec.latitude is not None and rec.longitude is not None:
                rec.geo_wkt = 'POINT(%s %s)' % (rec.longitude, rec.latitude)
            else:
                rec.geo_wkt = False

    def sync_to_postgis(self):
        """
        Optional: synchronize `geo_wkt` into a real PostGIS geometry column named `geom` (type geometry)
        in the `customer_map` table. This method will only run when the current db has PostGIS.

        NOTE: You must create the column `geom geometry` in PostgreSQL beforehand, or adapt the SQL.
        """
        self.flush()
        cr = self.env.cr
        # quick check for PostGIS availability
        try:
            cr.execute("SELECT postgis_full_version();")
            postgis_ok = True
        except Exception:
            postgis_ok = False
        if not postgis_ok:
            raise UserError(_('PostGIS not available on this database. Install extension postgis first.'))

        for rec in self:
            if not rec.geo_wkt:
                continue
            # SRID 4326 used here; change if you use different SRID
            sql = "UPDATE %s SET geom = ST_SetSRID(ST_GeomFromText(%s), 4326) WHERE id = %s" % (
                'customer_map',
                cr.literal(rec.geo_wkt),
                int(rec.id),
            )
            try:
                cr.execute(sql)
            except Exception as e:
                _logger.exception('Failed to sync geom for %s: %s', rec.id, e)
                raise UserError(_('Failed to sync geometry: %s') % e)
        return True
