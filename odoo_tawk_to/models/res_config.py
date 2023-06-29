# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import api, models, fields

import logging
_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
	_inherit = "res.config.settings"
	

	tawk_site_id = fields.Char(
		string="Tawk Site ID",
		help="Enter the Tawk To site id here."
		)
	visible_on = fields.Selection(
	   [('backend','Backend'),
	   ('website','Website'),
	   ('both','Both')],
		default="both",
		string="Visible On",
		 help="Select where you want to display the tawk to chat board")

	
	@api.multi
	def set_values(self):
		super(ResConfigSettings, self).set_values()
		IrDefault = self.env['ir.default'].sudo()
		IrDefault.set('res.config.settings','tawk_site_id', self.tawk_site_id)
		IrDefault.set('res.config.settings','visible_on', self.visible_on or 'both')

	@api.multi
	def get_values(self):
		res = super(ResConfigSettings, self).get_values()
		IrDefault = self.env['ir.default'].sudo()
		res.update({
			'tawk_site_id':IrDefault.get('res.config.settings','tawk_site_id', self.tawk_site_id),
			'visible_on':IrDefault.get('res.config.settings', 'visible_on', self.visible_on) or 'both'
		})
		return res