# -*- coding: utf-8 -*-
# Copyright (C) 2017 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo
from odoo import http
from odoo.http import request
from odoo.addons.laze_customize.controllers.main import WebsiteSale


class HideOnWebsite(WebsiteSale):

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        #Check for attributes
        response = super(HideOnWebsite, self).shop(page=page, category=category, search=search,ppg=ppg, **post)
        #Check for attribute hide boolean
        filtered_attribute_list = []
        for attrib in response.qcontext['attributes']:
            if not attrib.hide_on_website:
                filtered_attribute_list.append(attrib)
        response.qcontext['attributes'] = filtered_attribute_list


        return response
