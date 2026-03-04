from odoo import fields, models,api


class ResPartner(models.Model):
    """ @inherit partner model to add fields for report styles """
    _inherit = 'res.partner'

    cust_code = fields.Char(string="Customer Code")

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        # Call the original _name_search function to get the initial search result
        partner_ids = super(ResPartner, self)._name_search(name=name, args=args, operator=operator, limit=limit,
                                                           name_get_uid=name_get_uid)

        # Add your additional search criteria here
        if name and args:
            extra_domain = [('cust_code', operator, name)]
            partner_ids += list(self._search(args + extra_domain, limit=limit))

        return partner_ids