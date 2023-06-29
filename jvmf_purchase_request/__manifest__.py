# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl-3.0).

{
    "name": "Purchase Request",
    "author": "Eficent Business and IT Consulting Services S.L., "
              "Odoo Community Association (OCA), "
              "Mod Fuel LLC.",
    "version": "12.0.1.0.0",
    "summary": "Use this module to have notification of requirements of "
               "materials and/or external services and keep track of such "
               "requirements.",
    "category": "Purchases",
    "depends": [
        "purchase",
        "product",
        "purchase_stock",
        "jvmf_asset_management",
        "jvmf_purchasing_enhancements",
    ],
    "data": [
        "security/purchase_request.xml",
        "security/ir.model.access.csv",
        "data/purchase_request_sequence.xml",
        "data/purchase_request_data.xml",
        "views/purchase_request_view.xml",
        "reports/report_purchaserequests.xml",
        "views/purchase_request_report.xml",
        "views/res_partner.xml",
        "views/purchase.xml",
        "views/stock_views.xml"
    ],
    'demo': [
        "demo/purchase_request_demo.xml",
    ],
    "license": 'LGPL-3',
    'installable': True
}
