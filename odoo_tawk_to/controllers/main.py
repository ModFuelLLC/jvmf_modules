# -*- coding: utf-8 -*-
#################################################################################
#
# Copyright (c) 2018-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>:wink:
# See LICENSE file for full copyright and licensing details.
#################################################################################

from odoo import http
from odoo.http import request
from odoo import SUPERUSER_ID
from odoo.addons.web.controllers.main import WebClient, Binary, Home
import werkzeug.utils
import logging
import odoo
import json
_logger = logging.getLogger(__name__)

class Home(Home):


    @http.route('/wk/tawk/to/', type='json', auth='public')
    def wk_tawk_to(self, **kw):
        ir_default = request.env['ir.default'].sudo()
        tawk_site_id = ir_default.get(
            'res.config.settings', 'tawk_site_id')
        visible_on = ir_default.get(
            'res.config.settings', 'visible_on')
        if tawk_site_id:
            request.session['wk_tawk_to_site_id'] = tawk_site_id
            request.session['wk_tawk_visible_on'] = visible_on
            tz = 'None' if 'tz' not in request.session['context'] else request.session['context']['tz']
            vals = {
                'uid': request.session['uid'],
                'db': request.session['db'],
                'login': request.session['login'],
                'session_token': request.session['session_token'],
                'sale_order_id': request.session['sale_order_id'],
                'wk_tawk_visible_on': request.session['wk_tawk_visible_on'],
                'wk_tawk_to_site_id': request.session['wk_tawk_to_site_id'],
                'context': {
                    'lang': request.session['context']['lang'],
                    'tz': tz,
                },
                'geoip': request.session['geoip'],
            }
            _logger.info('----------------------------%r',vals)
            return True
        return False
