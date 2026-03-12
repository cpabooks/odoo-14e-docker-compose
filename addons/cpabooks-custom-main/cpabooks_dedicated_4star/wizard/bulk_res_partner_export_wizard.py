from odoo import api, models, fields, _
import io
import base64
import xlsxwriter
import xlrd
from odoo.exceptions import UserError, ValidationError


class BulkResPartnerExportWizard(models.TransientModel):
    _name = 'bulk.res.partner.export.wizard'
    _description = 'Bulk Contact Data Export Wizard'

    line_ids = fields.One2many('bulk.res.partner.export.line', 'wizard_id', string='Fields')

    available_field_ids = fields.One2many(
        'bulk.res.partner.export.line',
        'wizard_id',
        string='Available Fields',
        domain=[('state', '=', 'available')]
    )

    selected_field_ids = fields.One2many(
        'bulk.res.partner.export.line',
        'wizard_id',
        string='Selected Fields',
        domain=[('state', '=', 'selected')]
    )

    import_file = fields.Binary('Excel')
    import_filename = fields.Char("Filename")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        partner_fields = self.env['ir.model.fields'].search([
            ('model_id.model', '=', 'res.partner.extra'),
            ('store', '=', True)
        ])
        lines = []
        for field in partner_fields:
            state = 'selected' if field.name in (
                'partner_name', 'payment_terms_id', 'customer_code', 'care_of', 'whatsapp_number',
            ) else 'available'
            lines.append((0, 0, {
                'field_id': field.id,
                'state': state,
            }))

        # ✅ Attach lines to wizard
        res['line_ids'] = lines
        return res

    def action_export(self):
        selected_fields = self.selected_field_ids.mapped('field_name')
        if not selected_fields:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'No Fields Selected',
                    'message': 'Please select at least one field to export.',
                    'type': 'danger',
                }
            }

        # 1. Run query for selected fields
        query = f"SELECT {', '.join(selected_fields)} FROM res_partner_extra"
        self.env.cr.execute(query)
        rows = self.env.cr.fetchall()

        # 2. Create Excel in memory
        file_data = io.BytesIO()
        workbook = xlsxwriter.Workbook(file_data, {'in_memory': True})
        worksheet = workbook.add_worksheet("Partner Extra")

        # Write headers
        for col, field in enumerate(selected_fields):
            worksheet.write(0, col, field)

        # Write rows
        for row_idx, row in enumerate(rows, start=1):
            for col_idx, value in enumerate(row):
                worksheet.write(row_idx, col_idx, value or '')

        workbook.close()
        file_data.seek(0)

        # 3. Save as attachment
        export_file = base64.b64encode(file_data.read())
        file_name = f"partner_extra_{fields.Datetime.now()}.xlsx"

        attachment = self.env['ir.attachment'].create({
            'name': file_name,
            'type': 'binary',
            'datas': export_file,
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        # 4. Return download link
        download_url = f"/web/content/{attachment.id}?download=true"
        return {
            'type': 'ir.actions.act_url',
            'url': download_url,
            'target': 'self',
        }

    # IMPORT FILES
    def action_import_res_partner_extra(self):
        self.ensure_one()
        if not self.import_file:
            raise UserError("Please upload an Excel file to import.")

        # 1. Decode uploaded file
        file_content = base64.b64decode(self.import_file)

        # 2. Open workbook using xlrd
        try:
            workbook = xlrd.open_workbook(file_contents=file_content)
        except Exception as e:
            raise UserError(f"Failed to read Excel file: {str(e)}")

        sheet = workbook.sheet_by_index(0)  # first sheet

        if sheet.nrows < 2:
            raise UserError("The uploaded Excel file has no data.")

        # 3. Read header row
        headers = [sheet.cell_value(0, col).strip() for col in range(sheet.ncols)]

        # 4. Read data rows
        data_rows = []
        for row_idx in range(1, sheet.nrows):
            row_values = [sheet.cell_value(row_idx, col) for col in range(sheet.ncols)]
            data_rows.append(dict(zip(headers, row_values)))

        # 5. Prepare model field type mapping
        def get_field_type(f):
            if isinstance(f, fields.Many2one):
                return 'many2one'
            elif isinstance(f, fields.One2many):
                return 'one2many'
            elif isinstance(f, fields.Many2many):
                return 'many2many'
            elif isinstance(f, fields.Char):
                return 'char'
            elif isinstance(f, fields.Text):
                return 'text'
            elif isinstance(f, fields.Integer):
                return 'integer'
            elif isinstance(f, fields.Float):
                return 'float'
            elif isinstance(f, fields.Boolean):
                return 'boolean'
            elif isinstance(f, fields.Date):
                return 'date'
            elif isinstance(f, fields.Datetime):
                return 'datetime'
            else:
                return 'other'

        model_fields = self.env['res.partner.extra']._fields
        fields_info = {name: get_field_type(f) for name, f in model_fields.items()}

        # 6. Create / update res.partner.extra records
        created_count = 0
        Partner = self.env['res.partner']
        AdditionalInfo = self.env['res.partner.extra']

        for row in data_rows:
            partner_name = row.get('partner_name', '').strip()
            if not partner_name:
                continue  # skip if no partner name

            partner_id = Partner.sudo().search([('name', '=', partner_name)], limit=1)
            if not partner_id:
                continue

            # Prepare data dict
            create_data = {'partner_id': partner_id.id}

            for key, value in row.items():
                if key == 'partner_name':
                    continue  # already used for partner_id

                if key not in fields_info:  # ✅ Skip unknown fields
                    continue

                field_type = fields_info.get(key)

                # Convert empty strings to False for numeric/relational fields
                if field_type in ['many2one', 'integer', 'float', 'boolean'] and value == '':
                    create_data[key] = False
                else:
                    create_data[key] = value

            # Skip if no valid fields found
            if len(create_data.keys()) <= 1:  # only partner_id
                continue

            # Check if record exists
            additional_info = AdditionalInfo.sudo().search([('partner_id', '=', partner_id.id)], limit=1)
            if additional_info:
                additional_info.write(create_data)
            else:
                AdditionalInfo.create(create_data)
                created_count += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Import Completed',
                'message': f'Imported {created_count} rows from Excel.',
                'type': 'success',
            }
        }

    # Test Case
    def action_delete_res_partner_extra(self):
        additional_info_ids = self.env['res.partner.extra'].sudo().search([])
        for ad in additional_info_ids:
            ad.unlink()


    # -- NEW METHODS FOR 'ADD ALL' AND 'REMOVE ALL' BUTTONS --
    def add_all_fields(self):
        """Moves all available fields to the selected list."""
        self.available_field_ids.write({'state': 'selected'})

    def remove_all_fields(self):
        """Moves all selected fields back to the available list."""
        self.selected_field_ids.write({'state': 'available'})


class BulkResPartnerExportLine(models.TransientModel):
    _name = 'bulk.res.partner.export.line'
    _description = 'Line for Bulk Partner Export Wizard'
    _order = 'field_description'  # Order alphabetically by label

    wizard_id = fields.Many2one('bulk.res.partner.export.wizard', string='Wizard', required=True, ondelete='cascade')
    field_id = fields.Many2one('ir.model.fields', string='Field', required=True)
    # Related fields for display in the tree viewz
    field_description = fields.Char('Field Label', related='field_id.field_description', readonly=True)
    field_name = fields.Char('Technical Name', related='field_id.name', readonly=True)
    field_type = fields.Selection(related='field_id.ttype', readonly=True)

    state = fields.Selection([
        ('available', 'Available'),
        ('selected', 'Selected')
    ], string='Status', default='available', required=True)

    # -- NEW METHODS FOR PER-LINE BUTTONS --
    def move_to_selected(self):
        """Moves this specific line to the selected state."""
        self.ensure_one()
        self.state = 'selected'

    def move_to_available(self):
        """Moves this specific line to the available state."""
        self.ensure_one()
        self.state = 'available'
