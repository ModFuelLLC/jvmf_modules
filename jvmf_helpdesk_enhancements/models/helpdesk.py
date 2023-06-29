# -*- coding: utf-8 -*-
import datetime

from dateutil import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.addons.http_routing.models.ir_http import slug
from odoo.exceptions import UserError, ValidationError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def _default_team_id(self):
        team_id = self._context.get('default_team_id')
        if not team_id:
            team_id = self.env['helpdesk.team'].search([('member_ids', 'in', self.env.uid)], limit=1).id
        else:
            team_id = self.env['helpdesk.team'].search([], limit=1).id
        return team_id

    team_id = fields.Many2one('helpdesk.team', string='Helpdesk Team', default=_default_team_id, index=True, required=True)

    #added fields
    vendor_id = fields.Many2one('res.partner', string="Vendor", domain=[('supplier','=',True)])
    vendor_ref = fields.Char(string="Vendor Reference")
    sale_order = fields.Many2one('sale.order', string="Sale Order")
    purchase_order = fields.Many2one('purchase.order', string="Purchase Order")
    location = fields.Many2one('employment.locations', string="Location", domain=[('payroll_location','=',True)])
    department = fields.Many2one('hr.department', string="Department")

    #form control fields for additional fields
    view_vendor_form = fields.Boolean(related='team_id.view_vendor_form', readonly=True)
    view_vendor_ref_form = fields.Boolean(related='team_id.view_vendor_ref_form', readonly=True)
    view_sale_order_form = fields.Boolean(related='team_id.view_sale_order_form', readonly=True)
    view_purchase_order_form = fields.Boolean(related='team_id.view_purchase_order_form', readonly=True)
    view_location_form = fields.Boolean(related='team_id.view_location_form', readonly=True)
    view_department_form = fields.Boolean(related='team_id.view_department_form', readonly=True)

    #kanban control fields for additional Fields
    view_vendor_kanban = fields.Boolean(related='team_id.view_vendor_kanban', readonly=True)
    view_vendor_ref_kanban = fields.Boolean(related='team_id.view_vendor_ref_kanban', readonly=True)
    view_sale_order_kanban = fields.Boolean(related='team_id.view_sale_order_kanban', readonly=True)
    view_purchase_order_kanban = fields.Boolean(related='team_id.view_purchase_order_kanban', readonly=True)
    view_location_kanban = fields.Boolean(related='team_id.view_location_kanban', readonly=True)
    view_department_kanban = fields.Boolean(related='team_id.view_department_kanban', readonly=True)

class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.team"


    #form control fields for additional fields. Controls for all tickets in team
    view_vendor_form = fields.Boolean(string='Vendor')
    view_vendor_ref_form = fields.Boolean(string='Vendor Reference')
    view_sale_order_form = fields.Boolean(string='Sale Order')
    view_purchase_order_form = fields.Boolean(string='Purchase Order')
    view_location_form = fields.Boolean(string='Location')
    view_department_form = fields.Boolean(string='Department')

    #kanban control fields for additional fields.  Controls for all tickets in team
    view_vendor_kanban = fields.Boolean(string='Vendor Kanban')
    view_vendor_ref_kanban = fields.Boolean(string='Vendor Reference Kanban')
    view_sale_order_kanban = fields.Boolean(string='Sale Order Kanban')
    view_purchase_order_kanban = fields.Boolean(string='Purchase Order Kanban')
    view_location_kanban = fields.Boolean(string='Location Kanban')
    view_department_kanban = fields.Boolean(string='Department Kanban')

    #"""
    #Control methods to force select Useable if selected for view in kanban
    #Location
    @api.onchange('view_location_kanban')
    def _check_location_kanban(self):
        if self.view_location_kanban:
            self.view_location_form = True

    @api.onchange('view_location_form')
    def _check_location_form(self):
        if not self.view_location_form:
            self.view_location_kanban = False
    #Department
    @api.onchange('view_department_kanban')
    def _check_department_kanban(self):
        if self.view_department_kanban:
            self.view_department_form = True

    @api.onchange('view_department_form')
    def _check_department_form(self):
        if not self.view_department_form:
            self.view_department_kanban = False
    #"""
    #Vendor
    @api.onchange('view_vendor_kanban')
    def _check_vendor_kanban(self):
        if self.view_vendor_kanban:
            self.view_vendor_form = True

    @api.onchange('view_vendor_form')
    def _check_vendor_form(self):
        if not self.view_vendor_form:
            self.view_vendor_kanban = False

    #Vendor Ref
    @api.onchange('view_vendor_ref_kanban')
    def _check_vendor_ref_kanban(self):
        if self.view_vendor_ref_kanban:
            self.view_vendor_ref_form = True

    @api.onchange('view_vendor_ref_form')
    def _check_vendor_ref_form(self):
        if not self.view_vendor_ref_form:
            self.view_vendor_ref_kanban = False

    #Sale Order
    @api.onchange('view_sale_order_kanban')
    def _check_sale_order_kanban(self):
        if self.view_sale_order_kanban:
            self.view_sale_order_form = True

    @api.onchange('view_sale_order_form')
    def _check_sale_order_form(self):
        if not self.view_sale_order_form:
            self.view_sale_order_kanban = False

    #Purchase Order
    @api.onchange('view_purchase_order_kanban')
    def _check_purchase_order_kanban(self):
        if self.view_purchase_order_kanban:
            self.view_purchase_order_form = True

    @api.onchange('view_purchase_order_form')
    def _check_purchase_order_form(self):
        if not self.view_purchase_order_form:
            self.view_purchase_order_kanban = False
