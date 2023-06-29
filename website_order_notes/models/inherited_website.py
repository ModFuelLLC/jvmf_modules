# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import models, fields, api, _
from odoo import tools, api

from odoo.tools.translate import _


class website(models.Model):
    _inherit = 'website'

    def check_order_notes_setting(self, value=False):
        if value == 1:
            show_desire_date = self.env['ir.default'].sudo().get(
                'website.order.notes.settings', 'wk_show_desire_date')
            return show_desire_date
        if value == 2:
            show_notes_input = self.env['ir.default'].sudo().get(
                'website.order.notes.settings', 'wk_show_notes_input')
            return show_notes_input
        return False
