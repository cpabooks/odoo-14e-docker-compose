# -*- coding: utf-8 -*-

{
    "name": "CPA Books Database Lock",

    "summary": """
           This module will disable Select database button and Manage databases buttons from login screen.
           
           """,
    "description": """
           This module will disable Select database button and Manage databases buttons from login screen.
        """,
    'version': '15.0',
    "category": "web",
    "author": "cpabooks",
    "depends": [
        'web',
    ],
    "data": [

        "views/login_templates.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
