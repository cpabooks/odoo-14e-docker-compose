# -*- coding: utf-8 -*-
{
    'name': 'Review/Approve finishing/completion of tasks',
    'version': '1.0.01',
    'summary': """
        Approving finishing/completion of tasks by project manager or other user
    """,
    'category': 'Project',
    'author': 'XFanis',
    'support': 'odoo@xfanis.dev',
    'website': 'https://xfanis.dev/odoo.html',
    'license': 'OPL-1',
    'price': 10,
    'currency': 'EUR',
    'description':
        """
        Approving finishing/completion of tasks
        """,
    'data': [
        'data/project.xml',
        'views/project.xml',
        'views/helpdesk.xml',
        'views/helpdesk_review.xml',
    ],
    'depends': ['project','helpdesk'],
    'qweb': [],
    'images': [
        'static/description/project_task_approve.png',
        'static/description/form_setting.png',
        'static/description/raise_user_error.png',
        'static/description/kanban_card_button.png',
        'static/description/form_view_button.png',
        'static/description/kanban_card_approve.png',
        'static/description/form_view_approve.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
