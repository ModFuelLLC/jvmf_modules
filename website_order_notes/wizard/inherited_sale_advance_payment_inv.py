# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################
from odoo import api, fields, models, _
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp

class SaleAdvancePaymentInv(models.TransientModel):
	_inherit = "sale.advance.payment.inv"

	@api.multi
	def _create_invoice(self, order, so_line, amount):
		inv_obj = self.env['account.invoice']
		ir_property_obj = self.env['ir.property']

		account_id = False
		if self.product_id.id:
			account_id = self.product_id.property_account_income_id.id
		if not account_id:
			prop = ir_property_obj.get('property_account_income_categ_id', 'product.category')
			prop_id = prop and prop.id or False
			account_id = order.fiscal_position_id.map_account(prop_id)
		if not account_id:
			raise UserError(
				_('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
				(self.product_id.name,))

		if self.amount <= 0.00:
			raise UserError(_('The value of the down payment amount must be positive.'))
		if self.advance_payment_method == 'percentage':
			amount = order.amount_untaxed * self.amount / 100
			name = _("Down payment of %s%%") % (self.amount,)
		else:
			amount = self.amount
			name = _('Down Payment')

		invoice = inv_obj.create({
			'name': order.client_order_ref or order.name,
			'origin': order.name,
			'type': 'out_invoice',
			'reference': False,
			'account_id': order.partner_id.property_account_receivable_id.id,
			'partner_id': order.partner_invoice_id.id,
			'partner_shipping_id': order.partner_shipping_id.id,
			'invoice_line_ids': [(0, 0, {
				'name': name,
				'origin': order.name,
				'account_id': account_id,
				'price_unit': amount,
				'quantity': 1.0,
				'discount': 0.0,
				'uom_id': self.product_id.uom_id.id,
				'product_id': self.product_id.id,
				'sale_line_ids': [(6, 0, [so_line.id])],
				'invoice_line_tax_ids': [(6, 0, [x.id for x in self.product_id.taxes_id])],
				# 'account_analytic_id': order.project_id.id or False,
			})],
			'currency_id': order.pricelist_id.currency_id.id,
			'payment_term_id': order.payment_term_id.id,
			'fiscal_position_id': order.fiscal_position_id.id or order.partner_id.property_account_position_id.id,
			'team_id': order.team_id.id,
			'comment': order.note,
			'wk_invoice_notes':order.wk_notes,
			'desired_delivery_date':order.wk_desire_date,
		})
		invoice.compute_taxes()
		invoice.message_post_with_view('mail.message_origin_link',
					values={'self': invoice, 'origin': order},
					subtype_id=self.env.ref('mail.mt_note').id)
		return invoice