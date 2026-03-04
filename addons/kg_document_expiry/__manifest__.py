# -*- coding: utf-8 -*-
{
    "name": "Document Expiry",
    "summary": "Set Expiry Date for Document",
    "version": "14.0.1.0.0",
    'category': 'Productivity/Documents',
    'author': "Klystron Global",
    'maintainer': "Ashish Thomas",
    "license": "OPL-1",
    'website': 'https://www.klystronglobal.com',

    "depends": ["documents", "hr"],
    "data": [
        'views/email_template.xml',
        'views/documents_views.xml',
        'views/assets.xml',
        'views/cron_jobs.xml',
    ],
    'images': ['static/description/logo.png'],
    "installable": True,
}
