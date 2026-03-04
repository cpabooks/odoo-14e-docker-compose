from odoo import models, fields, api,_
from odoo.exceptions import ValidationError


class BillOfMaterialInheritance(models.Model):
    _inherit = 'mrp.bom'

    name = fields.Char(string='Number', required=True, copy=False, index=True, default=lambda self: _('New'))
    @api.model
    def create(self, vals_list):
        print(vals_list)
        res = super(BillOfMaterialInheritance, self).create(vals_list)
        get_sequence = self.env['ir.sequence'].next_by_sequence_for('bom')
        if not get_sequence:
            raise ValidationError(_("Sequence is not set for CRM"))
        res.name = get_sequence or _('/')
        return res