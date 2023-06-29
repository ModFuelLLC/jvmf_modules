# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import models, fields, api, _

class account_invoice(models.Model):
	_inherit = "account.invoice"

	wk_invoice_notes = fields.Text('Notes')

	