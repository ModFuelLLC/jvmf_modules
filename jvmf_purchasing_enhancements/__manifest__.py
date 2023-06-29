# -*- coding: utf-8 -*-
{
    'name': "JVMF Purchasing Management",

    'summary': """
        Added functionality for purchasing management""",

    'description': """
		Added functionality for purchasing management
    """,

    'author': "Mod Fuel LLC",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '12.0.1.0',
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'purchase',
    ],

    # always loaded
    'data': [
        'views/templates.xml',
        'views/vendor_bill.xml',
        'views/res_partner.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],

}
