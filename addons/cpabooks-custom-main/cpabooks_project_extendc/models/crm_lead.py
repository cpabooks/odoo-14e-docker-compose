from odoo import api, models, fields, _

class CRMLead(models.Model):
    _inherit = 'crm.lead'

    def name_get(self):
        name_list = []
        for record in self:
            name = record.name
            if record.enquiry_number:
                name = record.enquiry_number
            name_list += [(record.id, name)]
        return name_list

    @api.model
    def name_search(self, name='', args=[], operator='ilike', limit=100):
        """
         Added name_search for purpose to search by name and rent type
        """
        args += ['|', ('name', operator, name), ('enquiry_number', operator, name)]
        cuur_ids = self.search(args, limit=limit)
        return cuur_ids.name_get()