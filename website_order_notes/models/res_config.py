# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import models, fields, api, _
from odoo.tools.translate import _
from odoo.exceptions import Warning


class WebsiteOrderNotesSettings(models.Model):
	_inherit = 'webkul.website.addons'
	_name = 'website.order.notes.settings'

	
	wk_show_notes_input =  fields.Boolean(string='Enable Order Message Field')
	wk_show_desire_date = fields.Boolean(string='Enable Desire Date Field')
	maxium_delivery_date = fields.Integer(string="Maximum Number Of Days", help="Maximum number of days from current date after which user will be restricted.")
	minimum_delivery_date = fields.Integer(string="Minimum Number Of Days", help="Minimum number of days from current date before which user will be restricted.")

	@api.multi
	def get_values(self):
		res = super(WebsiteOrderNotesSettings, self).get_values()
		IrDefault = self.env['ir.default'].sudo()
		res.update({
			'wk_show_notes_input':IrDefault.get('website.order.notes.settings','wk_show_notes_input'),
			'wk_show_desire_date':IrDefault.get('website.order.notes.settings','wk_show_desire_date'),
			'maxium_delivery_date':IrDefault.get('website.order.notes.settings','maxium_delivery_date'),
			'minimum_delivery_date':IrDefault.get('website.order.notes.settings','minimum_delivery_date'),
			
		})
		return res

	@api.multi
	def set_values(self):
		super(WebsiteOrderNotesSettings, self).set_values()
		IrDefault = self.env['ir.default'].sudo()
		IrDefault.set('website.order.notes.settings','wk_show_notes_input', self.wk_show_notes_input or True)
		IrDefault.set('website.order.notes.settings','wk_show_desire_date', self.wk_show_desire_date or True)
		IrDefault.set('website.order.notes.settings','maxium_delivery_date', self.maxium_delivery_date)
		IrDefault.set('website.order.notes.settings','minimum_delivery_date', self.minimum_delivery_date)
		return True