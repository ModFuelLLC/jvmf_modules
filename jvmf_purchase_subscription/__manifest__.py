# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Purchase Subscription',
    'summary': "An easy way to manage your provider's subscriptions.",
    'category': 'Purchases',
    'installable': True,
    'application': True,
    'license' : 'AGPL-3',
    'depends': ['base', 'account', 'analytic', 'purchase'],
    'data': [
        'data/ir_cron.xml',
        'data/purchase_subscription_data.xml',
        'security/ir.model.access.csv',
        'views/purchase_subscription_views.xml',
        'views/res_partner_views.xml',
        'views/product_template_views.xml',
        'views/vendor_bill.xml',
    ],
    'author': 'Sudokeys, Mod Fuel LLC.',
    'description':
    """
        This module is used to trigger a recurrency provider invoice :
            - rent
            - Telephone/ internet subscription
            - Any other regular payment that needs a recurrent invoice.
    """
}
