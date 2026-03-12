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
# ########COPYRIGHT#####
# © 2016 Bernard K Too<bernard.too@optima.co.ke>
"""
from odoo import api, fields, models


class DN(models.Model):
    """inventory model inherited to add more field for the reporting engine."""
    _inherit = ["stock.picking"]

    def get_ref(self):
        for rec in self:
            get_customer_ref=self.env['sale.order'].search([('name','=',rec.origin)]).client_order_ref
            return get_customer_ref
    def get_signature(self):
        get_model = self.env['ir.model'].sudo().search([('model', '=', 'signature.setup')])
        if get_model:
            get_signature_data = self.env['signature.setup'].search(
                [('model', '=', 'stock.picking'), ('company_id', '=', self.env.company.id)])
            return get_signature_data
        else:
            return []
    @api.model
    def _default_disclaimer(self):
        message = "1. Goods once sold, will not be returned or exchanged. \n2. Buyer must check Quantity - Quality at the time of delivery of materials."
        return message or ''

    disclaimer = fields.Text(string='Disclaimer', default=_default_disclaimer)

    @api.onchange('partner_id')
    def onchange_partner_style(self):
        """method to assign a style to a report based on the selected
        partner."""

        self.pk_style = self.partner_id.style or self.env.user.company_id.df_style or self.env.ref(
            'professional_templates.df_style_for_all_reports').id
        self.dn_style = self.partner_id.style or self.env.user.company_id.df_style or self.env.ref(
            'professional_templates.df_style_for_all_reports').id

    dn_style = fields.Many2one(
        'report.template.settings',
        'Delivery Note Style',
        help="Select style to use when printing the Delivery Note",
        default=lambda self: self.partner_id.style or self.env.user.company_id.
        df_style)
