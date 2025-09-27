# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import base64
import csv
import io
import logging

_logger = logging.getLogger(__name__)


class CustomerMapImportWizard(models.TransientModel):
    _name = 'customer.map.import.wizard'
    _description = 'Import Customer Locations from CSV'

    file_data = fields.Binary(string='CSV File', required=True)
    filename = fields.Char(string='Filename')
    delimiter = fields.Selection([
        (',', 'Comma (,)'),
        (';', 'Semicolon (;)'),
        ('\t', 'Tab'),
        ('|', 'Pipe (|)'),
    ], string='Delimiter', default=',', required=True)
    has_header = fields.Boolean(string='File has header row', default=True)
    update_existing = fields.Boolean(string='Update existing customers', default=False)

    # Preview fields
    preview_data = fields.Text(string='Preview', readonly=True)
    import_summary = fields.Text(string='Import Summary', readonly=True)

    def action_preview(self):
        """Preview the CSV data before import"""
        if not self.file_data:
            raise UserError(_('Please select a CSV file first.'))

        try:
            # Decode file
            data = base64.b64decode(self.file_data)
            csv_data = data.decode('utf-8')

            # Parse CSV
            reader = csv.reader(io.StringIO(csv_data), delimiter=self.delimiter)
            rows = list(reader)

            if not rows:
                raise UserError(_('The CSV file is empty.'))

            # Show preview (first 5 rows)
            preview_rows = rows[:6] if self.has_header else rows[:5]
            preview_text = []

            for i, row in enumerate(preview_rows):
                row_text = f"Row {i + 1}: {' | '.join(row)}"
                preview_text.append(row_text)

            self.preview_data = '\n'.join(preview_text)

            # Expected format info
            expected_format = """
Expected CSV Format:
- Column 1: Customer Name (required)
- Column 2: Description (optional)
- Column 3: Phone (optional)
- Column 4: Email (optional)
- Column 5: Latitude (required, decimal format)
- Column 6: Longitude (required, decimal format)

Example:
PT ABC,Main Office,+62-21-1234567,info@abc.com,-6.200000,106.816666
            """

            self.preview_data += expected_format

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'customer.map.import.wizard',
                'view_mode': 'form',
                'res_id': self.id,
                'target': 'new',
            }

        except Exception as e:
            raise UserError(_('Error reading CSV file: %s') % str(e))

    def action_import(self):
        """Import the CSV data"""
        if not self.file_data:
            raise UserError(_('Please select a CSV file first.'))

        try:
            # Decode file
            data = base64.b64decode(self.file_data)
            csv_data = data.decode('utf-8')

            # Parse CSV
            reader = csv.reader(io.StringIO(csv_data), delimiter=self.delimiter)
            rows = list(reader)

            if not rows:
                raise UserError(_('The CSV file is empty.'))

            # Skip header if present
            if self.has_header and len(rows) > 0:
                rows = rows[1:]

            # Import data
            created_count = 0
            updated_count = 0
            error_count = 0
            errors = []

            CustomerMap = self.env['customer.map']

            for row_num, row in enumerate(rows, start=2 if self.has_header else 1):
                try:
                    if len(row) < 6:
                        raise ValidationError(_('Row must have at least 6 columns'))

                    name = row[0].strip()
                    description = row[1].strip() if len(row) > 1 else ''
                    phone = row[2].strip() if len(row) > 2 else ''
                    email = row[3].strip() if len(row) > 3 else ''

                    try:
                        latitude = float(row[4]) if row[4].strip() else 0.0
                        longitude = float(row[5]) if row[5].strip() else 0.0
                    except ValueError:
                        raise ValidationError(_('Invalid latitude or longitude format'))

                    if not name:
                        raise ValidationError(_('Customer name is required'))

                    # Validate coordinates
                    if not (-90 <= latitude <= 90):
                        raise ValidationError(_('Latitude must be between -90 and 90'))

                    if not (-180 <= longitude <= 180):
                        raise ValidationError(_('Longitude must be between -180 and 180'))

                    # Check if customer exists
                    existing = CustomerMap.search([('name', '=', name)], limit=1)

                    customer_data = {
                        'name': name,
                        'description': description,
                        'phone': phone,
                        'email': email,
                        'latitude': latitude,
                        'longitude': longitude,
                    }

                    if existing and self.update_existing:
                        existing.write(customer_data)
                        updated_count += 1
                    elif not existing:
                        CustomerMap.create(customer_data)
                        created_count += 1
                    elif existing and not self.update_existing:
                        errors.append(f"Row {row_num}: Customer '{name}' already exists")
                        error_count += 1

                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {row_num}: {str(e)}")
                    _logger.error("Import error on row %s: %s", row_num, str(e))

            # Prepare summary
            summary = [
                f"Import completed!",
                f"Created: {created_count} customers",
                f"Updated: {updated_count} customers",
                f"Errors: {error_count} rows",
            ]

            if errors:
                summary.append("\nErrors:")
                summary.extend(errors[:10])  # Show first 10 errors
                if len(errors) > 10:
                    summary.append(f"... and {len(errors) - 10} more errors")

            self.import_summary = '\n'.join(summary)

            # Show success message
            if created_count > 0 or updated_count > 0:
                message = f"Successfully imported {created_count + updated_count} customers"
                if error_count > 0:
                    message += f" ({error_count} errors)"

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Import Complete'),
                        'message': message,
                        'type': 'success' if error_count == 0 else 'warning',
                        'sticky': True,
                    }
                }
            else:
                raise UserError(_('No data was imported. Please check your file and try again.'))

        except Exception as e:
            raise UserError(_('Import failed: %s') % str(e))