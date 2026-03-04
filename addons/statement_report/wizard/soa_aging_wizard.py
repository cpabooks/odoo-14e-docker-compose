from odoo import api, models, fields


class SoaAgingWizard(models.TransientModel):
    _name = 'soa.aging.wizard'
    _description = 'SOA Aging Wizard'

    partner_id = fields.Many2one('res.partner', 'Partner', required=True)

    def action_partner_aging_statement(self):
        if self.partner_id:
            return {
                'name': self.partner_id.name,
                'type': 'ir.actions.act_window',
                'model': 'ir.actions.act_window',
                'res_model': 'res.partner',
                'view_mode': 'form',
                'res_id': self.partner_id.id
            }
        return {}