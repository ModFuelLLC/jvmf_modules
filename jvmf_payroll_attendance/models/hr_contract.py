# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class Contract(models.Model):
    _inherit = 'hr.contract'

    wage_type = fields.Selection([
        ('hour', 'Hour'),
        ('year', 'Year'),
        ('other', 'Other'),
    ], string='Wage Type', default='hour')

    @api.onchange('hybrid_joost_percent')
    @api.depends('hybrid_joost_percent')
    def _get_modfuel_percentage(self):
        for val in self:
            val.hybrid_modfuel_percent = 100 - val.hybrid_joost_percent

    #indicates if a contract is a joost, mod fuel or hybrid contract
    @api.depends('company_id')
    def _is_contract(self):
        for contract in self:
            contract.is_joost_contract = False
            contract.is_modfuel_contract = False
            if 'Joost Vapor LLC' == contract.company_name:
                contract.is_joost_contract = True
            if 'Mod Fuel LLC' == contract.company_name:
                contract.is_modfuel_contract = True
            if 'Joost Corp' == contract.company_name:
                contract.is_joost_contract = True
                contract.is_modfuel_contract = True

    other_wage_type = fields.Char("Other Wage Type")
    adp_joost_department_id = fields.Char('ADP Joost Contract Number', size=6)
    adp_modfuel_department_id = fields.Char('ADP Mod Fuel Contract Number', size=6)
    company_id = fields.Many2one('res.company', string='Company', required=True)
    company_name = fields.Char(related='company_id.name')
    hybrid_modfuel_percent = fields.Integer('Mod Fuel LLC %', compute='_get_modfuel_percentage',store=True, readonly=True)
    hybrid_joost_percent = fields.Integer('Joost Vapor LLC %')
    is_joost_contract = fields.Boolean(compute='_is_contract')
    is_modfuel_contract = fields.Boolean(compute='_is_contract')


    @api.constrains('hybrid_joost_percent')
    def check_hybrid_joost_percent(self):
        if self.hybrid_joost_percent < 0 or self.hybrid_joost_percent > 100:
            raise ValidationError(_('The value must be between 0 and 100'))
            return False
        return True

    @api.multi
    def get_employee_job_position(self):
        self.ensure_one()
        employee_obj = self.employee_id
        return {
            'contract_id': self.id,
            'job_id' : self.job_id.id if self.job_id else False,
            'job_name' : self.job_id.name if self.job_id else False,
            'employee_id' : employee_obj.id if employee_obj else False,
            'employee_name' : employee_obj.name if employee_obj else False,
        }

    @api.multi
    def get_hr_contract_state_change_wizard(self):
        context = dict(self._context) or {}
        context['active_ids'] = self.ids
        wizard = {
            'name':'Change Contract Status',
            'type':'ir.actions.act_window',
            'res_model':'hr.contract.wizard',
            'view_mode':'form',
            'view_type':'form',
            'view_id':self.env.ref('jvmf_payroll_attendance.hr_contract_wizard_form_view').id,
            'context' : context,
            'target':'new',
        }
        return wizard
