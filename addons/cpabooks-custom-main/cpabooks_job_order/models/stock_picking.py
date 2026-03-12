from odoo import fields, models, api, _
from odoo.exceptions import UserError


class StockPickingExtend(models.Model):
    _inherit = 'stock.picking'

    job_order_id=fields.Many2one('quotation.job.order')
    is_job_order_delivery=fields.Boolean()
    lpo_number = fields.Char(string="LPO")

    def get_ref(self):
        for rec in self:
            get_customer_ref=self.env['quotation.job.order'].search([('name','=',rec.origin)]).quotation_no.client_order_ref
            return get_customer_ref




    def button_validate(self):
        res=super(StockPickingExtend, self).button_validate()
        if self.is_job_order_delivery==True and self.picking_type_code=="outgoing":
                for job in self.job_order_id.order_line:
                    for delivery in self.move_ids_without_package:
                        if job.id == delivery.job_line_id.id and delivery.quantity_done>0:
                            job.delivered_qty += delivery.quantity_done
                            job.remaining_qty = job.product_uom_qty - job.delivered_qty
                            job.quotation_line_id.qty_delivered+=job.delivered_qty
                            # job.quotation_line_id.qty_to_invoice+=job.delivered_qty
                            job.quotation_line_id.invoice_status='to invoice'
                            job.quotation_line_id.order_id.invoice_status='to invoice'
        if self.is_job_order_delivery == True and self.picking_type_code == "incoming":
            for job in self.job_order_id.order_line:
                for delivery in self.move_ids_without_package:
                    if job.id == delivery.job_line_id.id and delivery.quantity_done > 0:
                        job.delivered_qty -= delivery.quantity_done
                        job.remaining_qty = job.product_uom_qty - job.delivered_qty
                        job.quotation_line_id.qty_delivered -=delivery.quantity_done
                        # job.quotation_line_id.qty_to_invoice-=delivery.quantity_done
                        get_sum_to_invoice=sum(job.quotation_line_id.order_id.order_line.mapped('qty_to_invoice'))
                        if job.quotation_line_id.qty_to_invoice>0:
                            job.quotation_line_id.invoice_status = 'to invoice'
                            job.quotation_line_id.order_id.invoice_status = 'to invoice'
                        if get_sum_to_invoice>0:
                            job.quotation_line_id.order_id.invoice_status = 'to invoice'
                        else:
                            job.quotation_line_id.invoice_status = 'no'
                            job.quotation_line_id.order_id.invoice_status = 'no'

        return res



class StockMoveExtend(models.Model):
    _inherit = 'stock.move'

    job_line_id=fields.Many2one('quotation.job.order.line')
    quotation_line_id = fields.Many2one('sale.order.line')

# class StockImmediateTransferExtend(models.TransientModel):
#     _inherit = 'stock.immediate.transfer'
#
#     def process(self):
#         pickings_to_do = self.env['stock.picking']
#         pickings_not_to_do = self.env['stock.picking']
#         for line in self.immediate_transfer_line_ids:
#             if line.to_immediate is True:
#                 pickings_to_do |= line.picking_id
#             else:
#                 pickings_not_to_do |= line.picking_id
#
#         for picking in pickings_to_do:
#             if picking.is_job_order_delivery==True and picking.picking_type_code=='outgoing':
#                 for job in picking.job_order_id.order_line:
#                     for delivery in picking.move_ids_without_package:
#                         if job.id == delivery.job_line_id.id:
#                             job.delivered_qty += delivery.product_uom_qty
#                             job.remaining_qty = job.product_uom_qty - job.delivered_qty
#                             job.quotation_line_id.qty_delivered = job.delivered_qty
#
#             if picking.is_job_order_delivery==True and picking.picking_type_code=='incoming':
#                 for job in picking.job_order_id.order_line:
#                     for delivery in picking.move_ids_without_package:
#                         if job.id == delivery.job_line_id.id:
#                             job.delivered_qty -= delivery.product_uom_qty
#                             job.remaining_qty = job.product_uom_qty - job.delivered_qty
#                             job.quotation_line_id.qty_delivered = job.delivered_qty
#
#             # If still in draft => confirm and assign
#             if picking.state == 'draft':
#                 picking.action_confirm()
#                 if picking.state != 'assigned':
#                     picking.action_assign()
#                     if picking.state != 'assigned':
#                         raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
#             for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
#                 for move_line in move.move_line_ids:
#                     move_line.qty_done = move_line.product_uom_qty
#
#         pickings_to_validate = self.env.context.get('button_validate_picking_ids')
#         if pickings_to_validate:
#             pickings_to_validate = self.env['stock.picking'].browse(pickings_to_validate)
#             pickings_to_validate = pickings_to_validate - pickings_not_to_do
#             return pickings_to_validate.with_context(skip_immediate=True).button_validate()
#         return True