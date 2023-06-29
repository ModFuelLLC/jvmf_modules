# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import datetime
import hashlib
import pytz
import threading
import re

from email.utils import formataddr

import requests
from lxml import etree
from werkzeug import urls

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.modules import get_module_resource
from odoo.osv.expression import get_unaccent_wrapper
from odoo.exceptions import UserError, ValidationError
from odoo.tools import pycompat

class Partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _compute_pr_ids(self):
        for rec in self:
            rec.pr_count = len(rec.pr_ids)

    purchase_request_allowed = fields.Boolean(string='Can Submit Purchase Requests')
    pr_ids = fields.One2many('purchase.request', 'partner_id', string='Purchase Requests associated with this Partner')
    pr_count = fields.Integer(compute='_compute_pr_ids', string='Purchase Requests')


    @api.multi
    def action_view_prs(self):
        action = self.env.ref('jvmf_purchase_request.purchase_request_form_action').read()[0]
        prs = self.mapped('pr_ids')
        if len(prs) > 1:
            action['domain'] = [('id', 'in', prs.ids)]
        elif prs:
            action['views'] = [(self.env.ref('jvmf_purchase_request.view_purchase_request_form').id, 'form')]
            action['res_id'] = prs.id
        return action
