# -*- coding: utf-8 -*-
{
    'name': "JVMF Project Management",

    'summary': """
        Project management enhancements""",

    'description': """
		Project management enhancements
    """,

    'author': "Mod Fuel LLC",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Project',
    'version': '12.0.1.0',
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'project',
        'project_native',
        'jvmf_purchase_request',
    ],

    # always loaded
    'data': [
        'views/project_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],

}
