# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import ValidationError


class Team(models.Model):
    _inherit = 'crm.team'

    stage_team_ids = fields.One2many('crm.stage.user', 'crm_team_id', string='Stage Assigned Salesperson')
    use_stage_assign = fields.Boolean(string='Stage Assign User')

    @api.constrains('use_stage_assign')
    def unset_stage_assign_users(self):
        if not self.use_stage_assign:
            for stage_user in self.stage_team_ids:
                stage_user = 0
