import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HrContractWizard(models.TransientModel):
    _name="hr.contract.wizard"

    @api.model
    def default_get(self,default_fields):
        res = super(HrContractWizard,self).default_get(default_fields)
        hr_contract_ids = self._context.get('active_ids',False)
        if hr_contract_ids:
            res['hr_contract_ids'] = hr_contract_ids
        return res

    hr_contract_ids = fields.Many2many("hr.contract")
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('pending', 'To Renew'),
        ('close', 'Expired'),
    ],string='New Status', help='Status of the contract', default='draft')


    @api.multi
    def status_change_confirmation(self):
        for rec in self:
            rec.hr_contract_ids.write({'state': rec.state})
