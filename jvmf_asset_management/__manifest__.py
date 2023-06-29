# -*- coding: utf-8 -*-
{
    'name': "JVMF Asset Management",

    'summary': """
        Tracks use of assets""",

    'description': """
        This module tracks the use of each asset.  It sets up a check out / check in system for each
        asset that then can be assigned to an employee or location for either short or long term loan.
    """,


    'author': "Mod Fuel LLC",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '12.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account_asset',
        'jvmf_purchasing_enhancements',
    ],

    # always loaded
    'data': [
        'security/security_view.xml',
        'security/ir.model.access.csv',
        'views/asset_management_views.xml',
        'views/account_asset_views.xml',
        'views/asset_accessories.xml',
        'data/asset_loan_sequence.xml',
        'data/ir_cron.xml',
        'views/templates.xml',
        'views/res_partner.xml',
        'views/product_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
