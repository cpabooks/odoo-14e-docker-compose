from odoo import fields, models, api

class DeliveredStatus(models.Model):
    _inherit = 'account.move'

    delivery_state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ('delivered', 'Delivered')
    ], string='Delivery Status', compute='_compute_state')

    @api.depends('delivery_state')
    def _compute_state(self):
        for rec in self:
            shipping_state = self.env['stock.picking'].search([('origin', '=', rec.invoice_origin)], limit=1)
            rec.delivery_state = shipping_state.state