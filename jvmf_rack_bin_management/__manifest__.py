# -*- coding: utf-8 -*-
# Copyright (C) 2012 - TODAY, Ursa Information Systems
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Rack, Shelf and Bin",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": 'Ursa Information Systems, Mod Fuel LLC.',
    'maintainer': 'Mod Fuel LLC.',
    'website': '',
    "category": 'Stock',
    "images": [],
    "depends": ["stock"],
    "data": [
        'views/stock_putaway_fixed_rule.xml',
        'views/product_view.xml',
        'views/stock_view.xml',
        'security/ir.model.access.csv',
        'security/ursa_rack_bin_management_security.xml',
    ],
    "test": [
    ],
    "auto_install": False,
    "application": False,
    "installable": True,
}
