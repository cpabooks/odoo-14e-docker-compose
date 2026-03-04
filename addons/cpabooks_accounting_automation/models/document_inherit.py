from odoo import fields, models, api


class DocumentInherit(models.Model):
    _name = "delete.document"

    @api.model
    def action_delete_document(self):
        installed_module_ids = self.env['ir.module.module'].search([('state', '=', 'installed'),('name','=','documents')])
        if installed_module_ids:
            query="""update documents_document set active={} where folder_id={} 
            and res_model='{}' and name in {}""".format(False,1,'documents.document',('Mails_inbox.pdf','Video: CpaBooks Documents',
            'invoice.png','city.jpg','people.jpg','Interior Design Brief.pdf'))
            self._cr.execute(query=query)

            query = """update documents_document set active={} where folder_id={} 
                         and name = '{}'""".format(False, 1,'Video: CpaBooks Documents')
            self._cr.execute(query=query)

