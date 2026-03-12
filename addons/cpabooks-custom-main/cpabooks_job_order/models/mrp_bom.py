import datetime

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import float_round



class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    date=fields.Date(string='Date',default=datetime.datetime.today())
    type = fields.Selection([
        ('normal', 'Manufacture this product'),
        ('phantom', 'Material supply')], 'BoM Type',
        default='normal', required=True)

    partner_id = fields.Many2one('res.partner', string='Customer')

    def get_signature(self):
        get_model = self.env['ir.model'].sudo().search([('model', '=', 'signature.setup')])
        if get_model:
            get_signature_data = self.env['signature.setup'].search(
                [('model', '=', 'mrp.bom'), ('company_id', '=', self.env.company.id)])
            return get_signature_data
        else:
            return []


class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    remarks=fields.Text(string="Remarks")