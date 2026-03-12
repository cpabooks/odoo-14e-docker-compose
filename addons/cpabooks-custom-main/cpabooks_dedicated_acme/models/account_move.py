from odoo import fields, models,api


class accountMove(models.Model):
    _inherit = 'account.move'



    @api.model
    def get_lpo(self):
        if self.invoice_origin:
            get_lpo_all = self.env['stock.picking'].sudo().search(
                [('origin', '=', self.invoice_origin), ('state', '=', 'done')])
            get_lpo = ""
            for rec in get_lpo_all:
                if not isinstance(rec.lpo_number,bool):
                    get_lpo += rec.lpo_number + ', '
            return get_lpo
        else:
            get_lpo = []