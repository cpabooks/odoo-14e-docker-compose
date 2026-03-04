# -*- coding: utf-8 -*-
"""
# License LGPL-3.0 or later (https://opensource.org/licenses/LGPL-3.0).
#
#This software and associated files (the "Software") may only be used (executed,
#modified, executed after modifications) if you have purchased a valid license
#from the authors, typically via Odoo Apps, or if you have received a written
#agreement from the authors of the Software (see the COPYRIGHT section below).
#
#You may develop Odoo modules that use the Software as a library (typically
#by depending on it, importing it and using its resources), but without copying
#any source code or material from the Software. You may distribute those
#modules under the license of your choice, provided that this license is
#compatible with the terms of the Odoo Proprietary License (For example:
#LGPL, MIT, or proprietary licenses similar to this one).
#
#It is forbidden to publish, distribute, sublicense, or sell copies of the Software
#or modified copies of the Software.
#
#The above copyright notice and this permission notice must be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
#ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#DEALINGS IN THE SOFTWARE.
#
#########COPYRIGHT#####
# © 2017 Bernard K Too<bernard.too@optima.co.ke>
"""
from odoo import fields, models,api, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    """ @inherit partner model to add fields for report styles """
    _inherit = 'res.partner'

    delivery_instructions = fields.Text("Delivery Instructions")
    style = fields.Many2one(
        'report.template.settings',
        'Reports Style',
        help="Select a style to use when printing reports for this customer",
        default=lambda self: self.env.user.company_id.df_style)

    #intercompany
    company_id = fields.Many2one(
        'res.company', 'Company', index=1)
    # cust_code = fields.Char(string='Customer Code')

    # company_id = fields.Many2one(
    #     'res.company', 'Company', index=1, related="create_uid.company_id")

    # @api.model
    # def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
    #     # Call the original _name_search function to get the initial search result
    #     partner_ids = super(ResPartner, self)._name_search(name=name, args=args, operator=operator, limit=limit,
    #                                                        name_get_uid=name_get_uid)
    #
    #     # Add your additional search criteria here
    #     if name and args:
    #         extra_domain = [('cust_code', operator, name)]
    #         partner_ids += list(self._search(args + extra_domain, limit=limit))

        # return partner_ids

    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            if rec.name:
                partner_rec = self.env['res.partner'].search(
                    [('name', '=', rec.name), ('id', '!=', rec.id)])
                if partner_rec:
                    raise UserError(_('Already exists with same name'))



