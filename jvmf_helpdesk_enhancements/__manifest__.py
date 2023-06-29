# -*- coding: utf-8 -*-
{
    'name': "JVMF Helpdesk Enhancements",

    'summary': """
        Added funcionality for Helpdesk""",

    'description': """
		Added funcionality for Helpdesk
    """,

    'author': "Mod Fuel LLC",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Helpdesk',
    'version': '12.0.1.0',
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'helpdesk',
        'hr',
        'jvmf_payroll_attendance',

    ],

    # always loaded
    'data': [
        'views/helpdesk_ticket_views.xml',
#        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
