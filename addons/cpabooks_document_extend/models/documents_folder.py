from odoo import models, fields,api


class DocumentsField(models.Model):
    _inherit = 'documents.folder'

    subfolders=fields.One2many('document.sub.folders','folder_id',string="Sub-Folders", copy=True)

    @api.model
    def create(self, vals_list):
        res=super(DocumentsField, self).create(vals_list)

        if res.subfolders:
            sub_folders=[]
            group_ids=[]
            read_group_ids=[]
            for group in res.group_ids:
                group_ids.append(group.id)
            for read_group in res.read_group_ids:
                read_group_ids.append(read_group.id)
            for line in res.subfolders:
                vals={
                    'name':line.name,
                    'company_id':res.company_id.id,
                    'parent_folder_id':res.id,
                    'group_ids':[(6,0,group_ids)],
                    'read_group_ids':[(6,0,read_group_ids)],
                    'user_specific':res.user_specific
                }
                test = self.env['documents.folder'].sudo().create(vals)
            #     sub_folders.append(vals)
            # if sub_folders:
            #     return super(DocumentsField, self).create(sub_folders)
            #     # test=self.env['documents.folder'].sudo().create(sub_folders)
            #     # return test
        return res




class DocumentsSubfolders(models.Model):
    _name = 'document.sub.folders'

    folder_id=fields.Many2one('documents.folder')
    name=fields.Char(string="Name")
