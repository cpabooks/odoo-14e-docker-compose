# -*- coding: utf-8 -*-
{
    'name': "CPABooks Custom Updates ",

    'summary': """
        Update Multiple Modules at a time.""",

    'description': """
            This module provides an efficient way to update or install multiple Odoo modules simultaneously, streamlining the process of managing module updates and installations.

            **How the Module Works:**
            - On the "Manage Update" page, the system launches a wizard where you can select the modules you want to update.
            - After selecting the desired modules, you can hit the "Update" button.
            - The module will:
                1. Update each selected module one by one.
                2. If a selected module is not installed, it will automatically install it.
            - Once the operation is completed, the module raises a wizard displaying a detailed result of the operation, showing which modules were successfully updated or installed, along with any errors encountered.

            **Features:**
            - Displays a summary of successfully updated and installed modules.
            - Tracks operation history for later reference:
              - A dedicated menu item, "Update History," provides access to the status page, where past updates are logged and can be reviewed at any time.
            - Simplifies module management, saving time for administrators by handling multiple module operations in one place.

            This module is especially useful for developers and administrators managing numerous custom or third-party modules, ensuring seamless updates and installations with minimal manual intervention.
        """,

    'author': "Tanvir Islam",
    'website': "https://www.cpabooks.org/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Update',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/update_multi_module_view.xml',
        'views/update_multi_module_addon_view.xml',
        'views/asset.xml',
        'data/sequences.xml',
        'data/create_default_module.xml',
        'wizard/update_result_wizard_vew.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,

}
