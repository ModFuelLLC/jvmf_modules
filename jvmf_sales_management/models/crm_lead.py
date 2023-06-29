# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.tools import email_re, email_split
from odoo.exceptions import UserError, AccessError

class Lead(models.Model):
    _inherit = "crm.lead"

    @api.onchange('team_id','stage_id')
    def _change_salesperson(self):
        stage_user_id = self.env['crm.stage.user'].search([('crm_team_id','=',self.team_id.id),('stage_id','=',self.stage_id.id)])
        if stage_user_id:
            self.user_id = stage_user_id[0].user_id

    @api.multi
    def _default_user_id(self):
        user_id = self.env.uid
        if 'default_team_id' in self.env.context and 'default_stage_id' in self.env.context:
            stage_user_ids =  self.env['crm.stage.user'].search([('crm_team_id','=',self.env.context['default_team_id']),('stage_id','=',self.env.context['default_stage_id'])])
            if stage_user_ids:
                user_id = stage_user_ids[0].user_id
        return user_id

    user_id = fields.Many2one('res.users',
        string='Assigned to',
        default=_default_user_id,
        track_visibility='always')
