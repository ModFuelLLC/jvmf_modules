import calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools import float_compare, float_is_zero

_AVAILABLITY_TYPES = [
    ('out', 'Checked Out'),
    ('req', 'Requested'),
    ('in', 'Available'),
    ('no_loan', 'No Loans'),
]


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    loan_availability = fields.Selection(_AVAILABLITY_TYPES, string="Loan Status",index=True, default='no_loan', readonly=True)
    can_be_loaned = fields.Boolean(string="Loan Allowed")
    asset_img = fields.Binary(string="Asset Image")
    estimated_eol = fields.Date(string="Estimated End of Life")
    barcode = fields.Char('Barcode')
    asset_loan_id = fields.Many2one('asset.loan', related='asset_loan_line_id.asset_loan_id', track_visibility=True, readonly=True)
    last_check_out = fields.Date(string="Checked out on", readonly=True)
    last_check_in = fields.Date(string="Returned on", readonly=True)
    asset_loan_line_id = fields.Many2one('asset.loan.line')
    asset_make = fields.Char(string='Asset Make/Brand')
    asset_model = fields.Char(string='Asset Model')
    repair = fields.Boolean(string='Out for repair')
    serial_number = fields.Char(string='Serial Number')
    product_id = fields.Many2one('product.template', string='Product')

    @api.multi
    @api.constrains('can_be_loaned')
    def _check_loanability(self):
        if self.can_be_loaned:
            self.loan_availability = 'in'
            if self.asset_loan_line_id.state in ['checked_out', 'over_due']:
                self.loan_availability = 'out'
            elif self.asset_loan_line_id.state in ['needs_approval','approved']:
                self.loan_availability = 'req'
        elif not self.can_be_loaned:
            if self.asset_loan_line_id.state in ['needs_approval','approved','checked_out', 'over_due']:
                raise ValidationError(_('%s is currently loaned out. Please wait till it has been returned.') % self.name)
            else:
                self.loan_availability = 'no_loan'

    @api.multi
    def action_view_loans(self):
        action = self.env.ref('jvmf_asset_management.asset_loan_action').read()[0]
        loan_ids = self.env['asset.loan.line'].search([('asset_id', '=', self.id)]).mapped('asset_loan_id')
        if len(loan_ids) > 1:
            action['domain'] = [('id', 'in', loan_ids.ids)]
        elif loan_ids:
            action['views'] = [(self.env.ref('jvmf_asset_management.jvmf_asset_loan_management_form_view').id, 'form')]
            action['res_id'] = loan_ids.id
        return action




class AccountAssetCategory(models.Model):
    _inherit = 'account.asset.category'

    user_ids = fields.Many2many('res.users','asset_loan_users_rel', 'asset_category_id', 'user_id', domain="[('share','=',False)]", string='Asset Managers')

class Users(models.Model):
    _inherit = 'res.users'

    #Many2many field to reference Asset Categories
    asset_category_ids = fields.Many2many('account.asset.category','asset_loan_users_rel', 'user_id', 'asset_category_id', string='Managed Assets')
