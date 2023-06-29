# -*- coding: utf-8 -*-
{
    'name': "JVMF Stock Enhancement",

    'summary': """
        Extends and enhances stock receipts.""",

    'description': """
        Enhancements Included
        \n1. Additional States
        \n\t - Follow Up Needed
        \n\t\t - Set to inform followers that there needs to be follow up on this item
        \n\t\t - Button not visible when in follow up state
        \n\t - Damaged
        \n\t\t - Set if item is received with damage
        \n\t\t - Button not visible when in damaged state
        \n\t - Set buttons for Reserve and Cancel to be visible when in both Follow up and Damaged
        \n\t - Set buttons to be visible only when receipt is 'incoming', and not the set states
        \n2. Setup automatic checks to see how long stock moves are in certain states
        \n\t - Set time frame (in days) in settings
        \n\t - Set recipient of followup notification in settings
        \n\t - Only checks incoming stock moves in states:
        \n\t\t - (waiting) Waiting Another Operation
        \n\t\t - (confirmed) Waiting Availabliity
        \n\t\t - (partially_available) Partially Available
        \n\t\t - (assigned) Available
        \n\t\t - (followup) Follow Up Needed
    """,

    'author': "Mod Fuel LLC",
    'website': "http://www.modfuelwholesale.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Stock',
    'version': '12.0.1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'stock',
        'delivery',
        'sale_stock',
        'mrp',
        'product',
        'jvmf_rma_management',
    ],

    # always loaded
    'data': [
        'data/ir_cron.xml',
        'views/stock_picking.xml',
        'views/res_config_settings.xml',
        'views/mail_templates.xml',
        'views/purchase_views.xml',
        'views/product_return_view.xml',
        'views/mrp_production_views.xml',
        'views/product.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
