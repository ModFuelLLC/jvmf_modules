# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
import math
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError, ValidationError, AccessError

# ('', ''),

_STATES = [
    ('new', 'New'),
    ('needs_approval', 'Needs Approval'),
    ('approved', 'Approved'),
    ('checked_out', 'Checked Out'),
    ('over_due', 'Over Due'),
    ('returned', 'Returned'),
    ('cancelled', 'Cancelled'),
    ('rejected', 'Rejected'),
]

_TYPES = [
    ('long', 'Long Term'),
    ('short', 'Short Term'),
]

class AssetLoan(models.Model):
    _name = 'asset.loan'
    _description = 'Asset Loan Management'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'resource.mixin']

    @api.model
    def _get_default_name(self):
        return self.env['ir.sequence'].next_by_code('asset.loan')

    @api.model
    def _compute_edit_due_date(self):
        for rec in self:
            rec.edit_due_date = self.env.user.has_group('jvmf_asset_management.group_asset_loan_manager')

    @api.model
    def _compute_edit_lines(self):
        for rec in self:
            rec.edit_lines = False
            if rec.state == 'new':
                rec.edit_lines = True
            elif rec.state == 'needs_approval' and self.env.user.has_group('jvmf_asset_management.group_asset_loan_manager'):
                rec.edit_lines = True

    name = fields.Char(string="Reference", default=_get_default_name,readonly=True, states={'new': [('readonly', False)]})
    state = fields.Selection(_STATES, string="Status", index=True, track_visibility=True, required=True, default='new', readonly=True)
    type = fields.Selection(_TYPES, string='Check Out Type', required=True, default='short', readonly=True, states={'new': [('readonly', False)]})
    partner_id = fields.Many2one('res.partner', domain=[('asset_loan_allowed', '=', True)], string="Partner", required=True, readonly=True, states={'new': [('readonly', False)]})
    check_out = fields.Date(string='Date Checked Out', readonly=True)
    check_in = fields.Date(string='Date Checked In', readonly=True)
    due_date = fields.Date(string='Due Date')
    over_due_warning = fields.Boolean(string="Warning")
    over_due = fields.Boolean(string="Over Due", readonly=True)
    edit_due_date = fields.Boolean(compute='_compute_edit_due_date')
    asset_loan_line_ids = fields.One2many('asset.loan.line', 'asset_loan_id', string='Assets')
    edit_lines = fields.Boolean(compute='_compute_edit_lines', default=True)
    needs_repair = fields.Boolean(string='Needs Repair')
    description = fields.Html(string='Description')

    @api.constrains('type', 'check_out')
    def _default_due_date(self):
        if self.check_out and not self.due_date and self.type == 'short':
            self.due_date = self.check_out + timedelta(days=7)

    @api.model
    def create(self,vals):
        loan = super(AssetLoan, self).create(vals)
        follower_ids = loan.asset_loan_line_ids.mapped('asset_id').mapped('category_id').mapped('user_ids').mapped('partner_id')
        follower_ids |= self.env.user.partner_id
        follower_ids |= loan.partner_id
        loan.message_subscribe(partner_ids=follower_ids.ids)
        return loan

    @api.multi
    def button_reset(self):
        #resets the request to new
        self.write({
            'state': 'new',
            'due_date': False,
            'check_out': False,
        })
        for line in self.asset_loan_line_ids:
            line.asset_id.write({'loan_availability': 'in',})
            line.write({'state': 'new',})

    @api.multi
    def button_to_approve(self):
        not_loanable_lines = self.asset_loan_line_ids.filtered(lambda line: line.asset_id.can_be_loaned == False)
        if not_loanable_lines:
            not_loanable_string = ''
            for line in not_loanable_lines:
                not_loanable_string += _('\n%s') % line.asset_id.name
            raise UserError(_('The following items are not available for loan: %s') % not_loanable_string)
        #sets the request to needs approval
        self.write({
            'state': 'needs_approval',
        })
        for line in self.asset_loan_line_ids:
            line.asset_id.write({'loan_availability': 'req',})
            line.write({'state': 'needs_approval',})

    @api.multi
    def button_approve(self):
        #approves the request, ready for check outgoing
        self.write({
            'state': 'approved',
        })
        for line in self.asset_loan_line_ids:
            line.write({'state': 'approved',})

    @api.multi
    def button_reject(self):
        #rejects the request
        self.write({
            'state': 'rejected',
        })
        self.asset_loan_line_ids.reject()

    @api.multi
    def button_check_out(self):
        #Marks the request as checked out and all that entails
        #sets check out date
        self.write({
            'state': 'checked_out',
            'check_out': fields.Date.today(),
        })
        self.asset_loan_line_ids.check_out()

    @api.multi
    def button_check_in(self):
        #checks the item(s) back in
        self.write({
            'state': 'returned',
            'check_in': fields.Date.today(),
        })
        for line in self.asset_loan_line_ids.filtered(lambda l: l.state == 'checked_out'):
            line.button_return()

    @api.multi
    def button_cancelled(self):
        #cancels the request
        self.write({
            'state': 'cancelled',
        })
        self.asset_loan_line_ids.cancel()

    @api.multi
    def button_renew(self):
        self.write({
            'state': 'checked_out',
            'over_due_warning': False,
            'over_due': False,
            'due_date': fields.Date.today() + timedelta(days=7),
        })
        self.asset_loan_line_ids.renew_line()
        body = _('%s has been renewed and is now due back on %s by the end of the work day or contact management.') % (self.name, self.due_date.strftime('%Y-%m-%d'))
        self.message_post(body=body)

    @api.multi
    def check_due_date(self):
        asset_loans = self.env['asset.loan'].search([('state', 'in', ('checked_out', 'over_due')), ('type', '=', 'short')])
        today = fields.Date.today()
        for loan in asset_loans:
            if loan.due_date == today:
                body = _('%s is due today.  Please return asset(s) by the end of the day or contact management.') % (loan.name)
                loan.message_post(body=body)
            elif loan.due_date < today:
                loan.write({
                    'state': 'over_due',
                    'over_due_warning': False,
                    'over_due': True,
                })

                self.asset_loan_line_ids.filtered(lambda l: l.state != 'returned').line_overdue()
                body = _('%s is over due.  Please return asset(s).') % (loan.name)
                loan.message_post(body=body)
            elif today >= (loan.due_date - timedelta(days=3)) and today <= loan.due_date:
                loan.over_due_warning = True
                body = _('%s is due in three days.  Please return asset(s) by then or contact management.') % (loan.name)
                loan.message_post(body=body)



class AssetLoanLine(models.Model):
    _name = 'asset.loan.line'

    asset_loan_id = fields.Many2one('asset.loan', string='Asset Loan')
    check_in =  fields.Date(string='Date Checked In', readonly=True)
    state = fields.Selection(_STATES, string='Line Status', index=True, track_visibility=True, required=True, default='new', readonly=True)
    asset_id = fields.Many2one('account.asset.asset', string='Asset', required=True, domain=[('loan_availability', '=', 'in'), ('can_be_loaned', '=', True)])
    asset_category = fields.Many2one('account.asset.category', related='asset_id.category_id', string='Asset Category')
    accessory_ids = fields.Many2many('asset.accessory', 'asset_accessory_rel', 'asset_line_id', 'accessory_id', string='Asset Accessories', domain="[('type_category','=',asset_category)]") #domain=lambda self: self._get_default_accessory_domain())
    estimated_eol = fields.Date(related='asset_id.estimated_eol', string="Estimated End of Life")
    partner_id = fields.Many2one('res.partner', related='asset_loan_id.partner_id', string='Partner')
    date_out = fields.Date(related='asset_loan_id.check_out', string='Date Checked Out')
    loan_type = fields.Selection(related='asset_loan_id.type', string='Loan Type')
    due_date = fields.Date(related='asset_loan_id.due_date', string='Due Date')

    @api.onchange('asset_id')
    def _get_default_accessories(self):
        self.accessory_ids = self.env['asset.accessory'].search([('accessory_type.category_id','=',self.asset_category.id),('default_accessory','=',True)])

    @api.model
    def create(self,vals):
        res = super(AssetLoanLine, self).create(vals)
        res.asset_id.asset_loan_line_id = res.id
        return res

    @api.model
    def line_overdue(self):
        for line in self:
            line.write({'state': 'over_due',})

    @api.multi
    def button_return(self):
        today = fields.Date.today()
        self.asset_id.write({
            'loan_availability': 'in',
            'last_check_in': today,
            'last_check_out': False,
            'repair': False,
            'asset_loan_line_id': 0,
        })
        self.write({
            'state': 'returned',
            'check_in': today,
        })
        line_states = list(set(self.asset_loan_id.asset_loan_line_ids.mapped('state')))
        if len(line_states) == 1 and 'returned' in line_states:
            self.asset_loan_id.write({
                'state': 'returned',
                'check_in': fields.Date.today(),
            })


    @api.model
    def check_out(self):
        today = fields.Date.today()
        for line in self:
            line.asset_id.write({
                'loan_availability': 'out',
                'last_check_out': today,
                'last_check_in': False,
                'repair': line.asset_loan_id.needs_repair,
            })
            line.write({
                'state': 'checked_out',
                'check_out': today,
            })

    @api.model
    def renew_line(self):
        today = fields.Date.today()
        for line in self.filtered(lambda l: l.state in ['checked_out', 'over_due']):
            line.asset_id.write({
                'loan_availability': 'out',
                'last_check_out': today,
            })
            line.write({
                'state': 'checked_out',
                'check_out': today,
            })

    @api.model
    def cancel(self):
        for line in self:
            line.asset_id.write({
                'loan_availability': 'in',
                'asset_loan_line_id': 0,
            })
            line.write({'state': 'cancelled',})

    @api.model
    def reject(self):
        for line in self:
            line.asset_id.write({
                'loan_availability': 'in',
                'asset_loan_line_id': 0,
            })
            line.write({'state': 'rejected',})


class AssetAccessoriesType(models.Model):
    _name = 'asset.accessory.type'
    _description = 'Asset Accessory Type'

    description = fields.Char(string='Description', required=True)
    category_id = fields.Many2one('account.asset.category', string='Asset Accessory Type Category', required=True)

    @api.multi
    def name_get(self):
        result = []
        for type in self:
            name = _("%s: %s") % (type.category_id.name, type.description)
            result.append((type.id, name))
        return result

class AssetAccessories(models.Model):
    _name = 'asset.accessory'
    _description = 'Asset Accessory'

    description = fields.Char(string='Description', required=True)
    accessory_type = fields.Many2one('asset.accessory.type', string="Accessory Type", required=True)
    type_category = fields.Many2one('account.asset.category', related='accessory_type.category_id')
    asset_lines = fields.Many2many('asset.loan.line', 'asset_accessory_rel', 'accessory_id', 'asset_line_id', string='Assets', readonly=True)
    default_accessory = fields.Boolean(string='Default Accessory')

    @api.multi
    def name_get(self):
        result = []
        for accessory in self:
            name = _("%s: %s") % (accessory.accessory_type.description, accessory.description)
            result.append((accessory.id, name))
        return result
