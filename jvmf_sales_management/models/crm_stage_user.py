# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class CRMStageUser(models.Model):
    _name = 'crm.stage.user'

    stage_id = fields.Many2one('crm.stage', string="CRM Stage", domain=lambda self: self._get_stage_domain())
    user_id = fields.Many2one('res.users', string="Assign To", domain=lambda self: self._get_user_domain())
    crm_team_id = fields.Many2one('crm.team', string="Sales Team")


    @api.model
    def _get_stage_domain(self):
        team = 0
        if 'params' in self.env.context and 'id' in self.env.context['params']:
            team = self.env.context['params']['id']
        stages = self.env['crm.stage.user'].search([('crm_team_id','=',team)]).mapped('stage_id').mapped('id')
        return [('id','not in',stages),'|',('team_id','=',False),('team_id','=',team)]

    @api.model
    def _get_user_domain(self):
        team = 0
        if 'params' in self.env.context and 'id' in self.env.context['params']:
            team = self.env.context['params']['id']
        return [('sale_team_id','=', team)]
