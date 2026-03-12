# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    project_id = fields.Many2one('project.project', string='Job Order')
    partner_id = fields.Many2one('res.partner', string='Customer')
    bom_reference = fields.Char(string='BOM Reference', related='bom_id.name')
    po_count=fields.Integer(compute="_compute_pr")

    def _compute_pr(self):
        if self.name:
            count = self.env['purchase.order'].search_count(
                [('mo_id', '=', self.id)])
            self.po_count = count

    def action_view_relavent_po(self):
        return {
            'name': _('Requests for Quotation'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('mo_id', '=', self.id)],

        }

    def action_create_qc(self):
        self.env['quality.check'].create({
            'product_id': self.product_id.id,
            'production_id': self.id,
            'company_id': self.company_id.id,
            'team_id': self.env['quality.alert.team'].search([], limit=1).id,
            'test_type_id': self.env.ref('quality_control.test_type_passfail').id,
        })

    def action_create_pr(self):
        print("**")

    # def _get_move_raw_values(self, product_id, product_uom_qty, product_uom, operation_id=False, bom_line=False):
    #     data=super(MrpProduction, self)._get_move_raw_values( product_id, product_uom_qty, product_uom, operation_id=False, bom_line=False)
    #     data['product_qty']=product_uom_qty
    #     return data

    def write(self,val_list):
        if 'product_qty' in val_list:
            val_list['product_qty']=self.product_qty
        return super(MrpProduction, self).write(val_list)

    # def action_confirm(self):
    #     super(MrpProduction, self).action_confirm()
    #
    #     for rec in self.move_raw_ids:
    #         if not rec.production_id:
    #             rec.production_id=self.id
    #             rec.raw_material_production_id=self.id


