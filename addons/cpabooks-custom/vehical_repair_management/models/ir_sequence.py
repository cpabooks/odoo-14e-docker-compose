from odoo import api, models, fields, _


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    sequence_for = fields.Selection(
        selection_add=[
            ('vehicle_service', 'Vehicle Service'),
        ],
        string="Sequence For",
    )


    @api.model
    def action_create_sequence_for_vehicle(self):
        get_all_company = self.env['res.company'].sudo().search([])

        for com in get_all_company:
            existing_vehicle_service_seq = self.env['ir.sequence'].sudo().search([
                ('sequence_for', '=', 'vehicle_service'),
                ('company_id', '=', com.id)
            ])

            # Only create the sequence if it doesn't exist
            if not existing_vehicle_service_seq:
                vehicle_service_vals = {
                    'name': 'Vehicle Service Sequence',
                    'sequence_for': 'vehicle_service',
                    'sequence_pattern': 'month_year_monthly',
                    'company_id': com.id,
                    'prefix': f'JOB/CO{str(com.id)}/%(year)s/%(month)s/',
                    'padding': 4,
                    'number_increment': 1,
                    'number_next_actual': 1
                }
                # Create the vehicle_service sequence
                self.env['ir.sequence'].create(vehicle_service_vals)




class SetCompanyPrefix(models.Model):
    _inherit = 'set.company.prefix'


    def set_prefix(self):
        res = super(SetCompanyPrefix, self).set_prefix()
        name = 'Vehicle Service Sequence'
        sequence_for = 'vehicle_service'
        code = 'JOB'

        existing_seq = self.env['ir.sequence'].search([
            ('company_id', '=', self.env.company.id),
            ('sequence_for', '=', sequence_for)
        ], limit=1, order='id asc')

        if existing_seq:
            existing_seq.write({
                'prefix': f'{code}/{self.prefix}/%(year)s/%(month)s/'
            })
        else:
            vals = {
                'name': 'Vehicle Service Sequence',
                'sequence_for': 'vehicle_service',
                'sequence_pattern': 'month_year_monthly',
                'company_id': self.env.company.id,
                'prefix': f'{code}/{self.prefix}/%(year)s/%(month)s/',
                'padding': 4,
                'number_increment': 1,
                'number_next_actual': 1
            }
            self.env['ir.sequence'].sudo().create(vals)

        return res
