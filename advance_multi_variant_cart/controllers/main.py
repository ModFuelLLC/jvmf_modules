# -*- coding: utf-8 -*-

import base64

import werkzeug
import werkzeug.urls

from odoo import http, SUPERUSER_ID
from odoo.http import request
import time
from odoo.tools.translate import _
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):


    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        res = super(WebsiteSale, self).shop(page, category, search, ppg, **post)
        if post.get('error_multi_cart'):
        	res.qcontext.update({"error_multi_cart" : 1})
        return res
    @http.route(['/shop/cart/update_json_multi_carty'], type='json', auth="public", website=True)
    def update_json_multi_carty(self, datas):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        return_context = 0
        if datas:
            for i in range(len(datas)):
                qty = float(datas[i]['qty'])
                if datas[i]['product_id'] and datas[i]['qty']:
                    line = request.website.sale_get_order(force_create=1)._cart_find_product_line(product_id = int(datas[i]['product_id']))
                    sale_order = request.website.sale_get_order(force_create=1)
                    order = sale_order.sudo().browse(sale_order.id)
                    product_id =  int(datas[i]['product_id'])              
                    if line:  
                        quantity = line.product_uom_qty
                        virtual_available =0  
                        variant =  request.env['product.product'].sudo().browse(product_id)                 
                        if variant.inventory_availability in ['always','never','threshold','custom']:
                            if variant.inventory_availability in ['always','threshold']:
                                virtual_available = variant.virtual_available
                                for line in order.order_line:   
                                    if line.product_id and line.product_id.id==variant.id:
                                        virtual_available = virtual_available - line.product_uom_qty
                            if variant.inventory_availability in ['never','custom'] or not variant.inventory_availability:
                                virtual_available = qty                                
                            if virtual_available>=1:
                                if qty<=virtual_available:
                                    virtual_available = qty
                            if qty>virtual_available:
                            	return_context = 1  
                        quantity = line.product_uom_qty + virtual_available                              

                        values = sale_order._website_product_id_change(sale_order.id, product_id, qty=quantity)
                        if sale_order.pricelist_id.discount_policy == 'with_discount' and not sale_order.env.context.get('fixed_price'):
                            order = sale_order.sudo().browse(sale_order.id)
                            product_context = dict(sale_order.env.context)
                            product_context.setdefault('lang', order.partner_id.lang)
                            product_context.update({
                                'partner': sale_order.partner_id.id,
                                'quantity': quantity,
                                'date': sale_order.date_order,
                                'pricelist': sale_order.pricelist_id.id,
                            })
                            product = request.env['product.product'].sudo().with_context(product_context).browse(product_id)
                            values['price_unit'] = request.env['account.tax']._fix_tax_included_price_company(
                                line._get_display_price(product),
                                line.product_id.taxes_id,
                                line.tax_id,
                                sale_order.company_id
                            )

                        line.write(values)
                    else:
                        request.website.sale_get_order(force_create=1)._cart_update(product_id=int(datas[i]['product_id']), add_qty=float(datas[i]['qty']))
        return return_context


        
    @http.route(['/shop/multi_cart'], type='http', auth="public", website=True)
    def update_cart_popup(self, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        if post.get('product_tmpl_id'):
            request.website.get_current_pricelist()
            order = request.website.sale_get_order(force_create=1)
            prod_obj = request.env['product.template']
            product_data = prod_obj.sudo().browse(int(post.get('product_tmpl_id')))
            if product_data:
                qty = 0
                for variant in product_data.product_variant_ids:
                    qty = 0
                    if post.get('qty-%s' % variant.id):
                        qty = float(post.get('qty-%s' % variant.id))
                        if qty >= 1:
                            if variant.inventory_availability in ['always','never','threshold','custom']:
                                virtual_available = 0
                                if variant.inventory_availability in ['always','threshold']:
                                    virtual_available = variant.virtual_available
                                    for line in order.order_line:   
                                        if line.product_id and line.product_id.id==variant.id:
                                            virtual_available = virtual_available - line.product_uom_qty
                                if variant.inventory_availability in ['never','custom'] or not variant.inventory_availability:
                                    virtual_available = qty                                
                                if virtual_available>=1:
                                    if qty<=virtual_available:
                                        virtual_available = qty                                
                                    request.website.sale_get_order(force_create=1)._cart_update(
                                product_id=int(variant.id), add_qty=float(virtual_available))
        return request.redirect('/shop/cart')
