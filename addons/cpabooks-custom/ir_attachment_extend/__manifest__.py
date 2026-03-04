{
    'name': 'Perview Attachment',
    'version': '14.0.0',
    'category': 'Tools',
    'summary': 'Preview File',
    'description': """
        This module Preview the file.
    """,
    'author': 'Nahid Jawad Angon',
    'website': '',
    'depends': ['base', 'mail', 'hr', 'product', 'professional_templates_v1'],
    'data': [
        'views/inherit_ir_attachment_kanban.xml',
        'views/config.xml',
        'views/product_template.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    'auto_install': False,
}
