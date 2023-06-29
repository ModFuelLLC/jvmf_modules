# -*- coding: utf-8 -*-
{
    'name': "JVMF Sales Management",

    'summary': """
        Added functionality for sales management""",

    'description': """
		Added functionality for sales management
    """,

    'author': "Mod Fuel LLC",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '12.0.0.0',
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'sale',
        'account',
        'product',
        'stock',
        'website_stock',
        'website_sale_delivery',
        'jvmf_stock_enhancements',
    ],

    # always loaded
    'data': [
        'views/crm_team_views.xml',
        'views/sales_views.xml',
        'views/res_partner.xml',
        'security/ir.model.access.csv',
        'security/jcv_security.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    "pre_init_hook":'pre_init_salesperson_update',
    "installable": True,

}
