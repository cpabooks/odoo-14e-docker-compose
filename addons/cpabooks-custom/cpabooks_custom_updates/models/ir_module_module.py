from odoo import api, models

class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    @api.model
    def name_search(self, name='', args=[], operator='ilike', limit=100):
        """
         Added name_search for purpose to search by name and rent type
        """
        args += ['|', ('name', operator, name), ('shortdesc', operator, name)]
        cuur_ids = self.search(args, limit=limit)
        return cuur_ids.name_get()

