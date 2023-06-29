# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################
{
  "name"                 :  "Odoo Livechat Tawk To",
  "summary"              :  "Embed live chat in Odoo using Tawk.to",
  "category"             :  "Extra Tools",
  "version"              :  "1.0.0",
  "sequence"             :  45,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://webkul.com/blog/odoo-livechat-tawk/",
  "description"          :  """https://store.webkul.com/Odoo-LiveChat-Tawk-To.html""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=odoo_tawk_to&version=12.0",
  "depends"              :  ['website'],
  "data"                 :  [
                             'views/res_config_view.xml',
                             'views/templates.xml',
                            ],
  "demo"                 :['data/demo.xml'],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  10,
  "currency"             :  "EUR",
  "pre_init_hook"        :  "pre_init_check",
}