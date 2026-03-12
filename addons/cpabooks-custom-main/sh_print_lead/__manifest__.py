# -*- coding: utf-8 -*-
{
    "name": "Print Lead Or Opportunity",

    "author": "Softhealer Technologies",

    "license": "OPL-1",

    "website": "https://www.softhealer.com",

    "support": "support@softhealer.com",

    "version": "14.0.2",

    "category": "Sales",

    "summary": "print opportunity app, print quotation list report, print lead meetings detail, print lead module, lead print, opportunity print, oppertunity print odoo",

    "description": """This module useful to print Lead. This module useful to print opportunity.""",

    "depends":  ['sale_management', 'crm'],

    "data": [
            "security/ir.model.access.csv",
            "views/crm_lead.xml",
            "reports/report_crm_print_lead.xml",
            "wizard/lead_op_xls_report_wizard.xml",
    ],
    "images": ["static/description/background.png", ],
    "live_test_url": "https://youtu.be/qFx72idYnCs",
    "installable": True,
    "application": True,
    "auto_install": False,

    "price": 15,
    "currency": "EUR"
}
