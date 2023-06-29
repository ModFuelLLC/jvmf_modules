# -*- coding: utf-8 -*-
# Copyright (C) 2017 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "JVMF RMA Management",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author":   "Open Source Integrators, "
                "Mod Fuel LLC.",
    "maintainer": "Mod Fuel LLC.",
    "website": "",
    "summary": "Return Merchandise Authorization (RMA) Management tracks and allows for both customer returns as well as vendor returns.",
    "category": "Purchases",
    "images": [],
    "depends": [
        "base",
        "purchase",
        "sale",
        "stock",
        "account",
        "jvmf_purchase_request",
    ],
    "data": [
        "data/ir_cron.xml",
        "security/security_view.xml",
        "security/ir.model.access.csv",
        "views/stock_view.xml",
        "views/account_invoice_view.xml",
        "views/product_return_view.xml",
        "views/product_return_report.xml",
        "views/report_product_return.xml",
        "views/res_config_settings.xml",
    ],
    "test": [
    ],
    "auto_install": False,
    "application": False,
    "installable": True,
}
