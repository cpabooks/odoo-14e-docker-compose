from odoo import fields, models,api


class SaleOrder(models.Model):
    _inherit= "sale.order"

    project_id = fields.Many2one('project.project', string='Job Order', readonly=False)
    is_project_create= fields.Boolean(string="Create Project?", default=True)
    show_project = fields.Boolean(default=True, string="Show Project")

    @api.onchange('company_id')
    def get_default_show_project(self):
        get_highest_qt = self.env['sale.order'].sudo().search(
            [('company_id', '=', self.company_id.id), ('state', '!=', 'cancel')],
            limit=1,
            order='id desc')
        if get_highest_qt:
            self.show_project = get_highest_qt.show_project

    def default_get(self, vals):
        res = super(SaleOrder, self).default_get(vals)
        get_top_sale=self.env['sale.order'].sudo().search([],order='id desc', limit=1)


        if get_top_sale:
            res.update({
                'is_project_create': get_top_sale.is_project_create
            })
        return res

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.is_project_create and not self.project_id:
            project_val = {
                'name': self.name,
                'label_tasks': "Task",
                'user_id': self.env.user.id,
                'partner_id': self.partner_id.id,
                'privacy_visibility': 'portal',

            }
            project = self.env['project.project'].sudo().create(project_val)

            analytic_acc_val = {
                'name': project.name,
                'partner_id': project.partner_id.id
            }
            analytic_acc = self.env['account.analytic.account'].sudo().create(analytic_acc_val)

            project.analytic_account_id = analytic_acc.id

            # self.project_name = project.name
            self.project_id = project.id
            self.analytic_account_id = project.analytic_account_id.id

    # def confirm_sale_order(self):
    #     res = super(SaleOrder, self).confirm_sale_order()
    #     if self.is_project_create and not self.project_id:
    #         project_val = {
    #             'name': self.name,
    #             'label_tasks': "Task",
    #             'user_id': self.env.user.id,
    #             'partner_id': self.partner_id.id,
    #             'privacy_visibility': 'portal',
    #
    #         }
    #         project = self.env['project.project'].sudo().create(project_val)
    #
    #         analytic_acc_val = {
    #             'name': project.name,
    #             'partner_id': project.partner_id.id
    #         }
    #         analytic_acc = self.env['account.analytic.account'].sudo().create(analytic_acc_val)
    #
    #         project.analytic_account_id = analytic_acc.id
    #
    #
    #         # self.project_name = project.name
    #         self.project_id = project.id
    #         self.analytic_account_id = project.analytic_account_id.id



    def _prepare_invoice(self):
        invoice_vals=super(SaleOrder, self)._prepare_invoice()
        invoice_vals['project_id']=self.project_id.id
        return invoice_vals

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_new_picking_values(self):
        res = super(StockMove, self)._get_new_picking_values()
        # Pass value of note field from Sales Order to Picking
        res.update({'project_id': self.group_id.sale_id.project_id.id})
        return res
