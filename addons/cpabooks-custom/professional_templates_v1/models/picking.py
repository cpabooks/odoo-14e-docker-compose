# -*- coding: utf-8 -*-
"""
# License LGPL-3.0 or later (https://opensource.org/licenses/LGPL-3.0).
#
# This software and associated files (the "Software") may only be used (executed,
# modified, executed after modifications) if you have purchased a valid license
# from the authors, typically via Odoo Apps, or if you have received a written
# agreement from the authors of the Software (see the COPYRIGHT section below).
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#
#########COPYRIGHT#####
# © 2017 Bernard K Too<bernard.too@optima.co.ke>
"""
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError, RedirectWarning

class PK(models.Model):
    """Inventory model inherited to add more fields and methods for the
    reporting templates module."""
    _inherit = ["stock.picking"]

    sender_id=fields.Many2one('res.partner')
    receiver_id=fields.Many2one('res.partner')

    pk_style = fields.Many2one(
        'report.template.settings',
        'Picking Style',
        help="Select Style to use when printing the picking slip",
        default=lambda self: self.partner_id.style or self.env.user.company_id.df_style)

    def action_confirm(self):
        res=super(PK, self).action_confirm()
        for rec in self:
            for line in rec.move_line_ids:
                line.prod_description=line.move_id.description_picking
        return res

    def button_validate(self):
        res=super(PK, self).button_validate()
        for rec in self:
            for line in rec.move_line_ids:
                line.prod_description=line.move_id.description_picking
        return res

    @api.model
    def create(self, vals):
        res = super(PK, self).create(vals)
        if res:  # trigger onchage after creating picking to update the partner style
            res.onchange_partner_style()
            if res.move_ids_without_package:
                for line in res.move_ids_without_package:
                    line.product_id.delivery_prod_description = line.description_picking
                    line.sale_line_id.delivery_description = line.description_picking
        return res


    def reserve_qty(self):
        for rec in self:
            for line in rec.move_line_ids_without_package:
                if line.product_id.tracking == 'serial':
                    get_stock_line = self.env['stock.quant'].sudo().search([('product_id', '=', line.product_id.id),
                                                                            ('location_id', '=', rec.location_id.id),
                                                                            ('company_id', '=', rec.company_id.id),
                                                                            ('lot_id', '=', line.lot_id.id)], limit=1)
                    if not get_stock_line:
                        raise ValidationError(_("Lot:" + line.lot_id.name + " does not exists in your stock"))
                    if get_stock_line and get_stock_line.quantity > 0 and get_stock_line.reserved_quantity == 0:
                        get_stock_line.reserved_quantity = 1

                if line.product_id.tracking == 'none':
                    get_stock_line = self.env['stock.quant'].sudo().search([('product_id', '=', line.product_id.id),
                                                                            ('location_id', '=', rec.location_id.id),
                                                                            ('company_id', '=', rec.company_id.id)],
                                                                           limit=1)
                    if not get_stock_line:
                        raise ValidationError(_("No Record Found for Product:\n" + line.product_id.name))
                    if get_stock_line and get_stock_line.quantity > 0 and get_stock_line.reserved_quantity < line.product_uom_qty and line.product_uom_qty + get_stock_line.reserved_quantity <= get_stock_line.quantity:
                        get_stock_line.reserved_quantity += line.product_uom_qty

    def action_set_quantities_to_reservation(self):
        if self.picking_type_code=="outgoing":
            for move in self.move_ids_without_package:
                if  move.has_tracking == 'none' :
                    if not move.move_line_ids:
                        move.move_line_ids+=self.env['stock.move.line'].sudo().create({
                            'product_id': move.product_id.id,
                            'product_uom_id': move.product_uom.id,
                            # 'product_uom_qty': line.product_uom_qty - line.delivered_qty,
                            'location_id': move.warehouse_id.lot_stock_id.id,
                            'location_dest_id': 5,
                            # 'state': 'assigned',
                            'description_picking': move.name,
                            'prod_description':move.description_picking,
                            'move_id':move.id,
                            'picking_id':self.id
                        })

            self.move_lines._set_quantities_to_reservation_for_sale()
        #     for line in self.move_ids_without_package.move_line_ids:
        #         rounding = line.product_id.uom_id.rounding
        #         quants = self.env['stock.quant']._gather(line.product_id, line.location_id, lot_id=False, package_id=False, owner_id=False,
        #                               strict=True)
        #         available_quantity = sum(quants.mapped('reserved_quantity'))
        #         if float_compare(abs(line.product_qty), available_quantity, precision_rounding=rounding) > 0:
        #             line.write({
        #                 'product_uom_qty':0,
        #                 'qty_done':line.product_uom_qty
        #             })

        else:
            self.move_lines._set_quantities_to_reservation()

    def write(self,vals):
        super(PK, self).write(vals)
        for rec in self:
            if rec.move_ids_without_package:
                for line in rec.move_ids_without_package:
                    line.product_id.delivery_prod_description = line.description_picking
                    line.sale_line_id.delivery_description = line.description_picking

