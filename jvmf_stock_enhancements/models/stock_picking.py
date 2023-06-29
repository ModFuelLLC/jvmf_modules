# -*- coding: utf-8 -*-
from collections import namedtuple
import json
import time

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'


	# add additional states to record: followup and damage
    state = fields.Selection(selection_add=[('followup', 'Follow Up Needed'), ('damaged', 'Damaged')],
        help=" * Draft: not confirmed yet and will not be scheduled until confirmed\n"
             " * Waiting Another Operation: waiting for another move to proceed before it becomes automatically available (e.g. in Make-To-Order flows)\n"
             " * Waiting Availability: still waiting for the availability of products\n"
             " * Partially Available: some products are available and reserved\n"
             " * Ready to Transfer: products reserved, simply waiting for confirmation.\n"
             " * Damaged: product arrived with damage.\n"
             " * Follow Up Needed: indicates that the delivery hasn't had any progress for a while. \n"
             " * Transferred: has been processed, can't be modified or cancelled anymore\n"
             " * Cancelled: has been cancelled, can't be confirmed anymore")

    #Add field to track when the state changes.
    state_change_date = fields.Datetime(string='DateTime State Last Changed',
        compute='set_change_date', store=True, readonly=True, index=True)

    #add incoming carrier information from purchase orders
    po_carrier_id = fields.Many2one('delivery.carrier', related="po_id.incoming_carrier_id", string='PO Carrier')
    po_carrier_tracking_ref = fields.Char(string=' PO Tracking Reference', related="po_id.incoming_carrier_tracking_ref")

    #add incoming carrier information from customer rmas
    crma_carrier_id = fields.Many2one('delivery.carrier', related="rma_id.incoming_carrier_id", string='RMA Carrier')
    crma_carrier_tracking_ref = fields.Char(string='RMA Tracking Reference', related="rma_id.incoming_carrier_tracking_ref")

    picking_type_name = fields.Char(related='picking_type_id.name', string='Picking Type Name')

    #set origin information
    sale_id = fields.Many2one('sale.order', related='move_lines.sale_line_id.order_id', string='SO #', index=True, readonly=True, help="Reference of the Sale Order")
    origin_is_visible = fields.Boolean(string='Visible', default=True, compute='_origin_visible')

    #select the responsible employee
    responsible_employee_id = fields.Many2one('hr.employee', string='Responsible Employee')

    @api.model
    def _origin_visible(self):
        for picking in self:
            if picking.sale_id:
                picking.origin_is_visible = False
            elif picking.po_id:
                picking.origin_is_visible = False
            elif picking.rma_id:
                picking.origin_is_visible = False


    @api.onchange('picking_type_id')
    def check_dropship_carrier(self):
        for picking in self:
            if picking.picking_type_id.name == 'Dropship':
                picking.purchasing_carrier_id = 8
                picking.crma_carrier_id = 0
            if picking.picking_type_id.code != 'outgoing':
                picking.carrier_id = 0

    @api.multi
    def write(self, vals):
        for picking in self:
            if picking.picking_type_id.name == 'Dropship':
                vals['purchasing_carrier_id'] = 8
                vals['crma_carrier_id'] = 0
            if picking.picking_type_id.code != 'outgoing':
                vals['carrier_id'] = 0
            if picking.picking_type_id.code == 'incoming' and picking.company_id.stock_followup_contact:
                follower_ids = []
                follower_ids.append(picking.company_id.stock_followup_contact.partner_id.id)
                if picking.owner_id:
                    follower_ids.append(picking.owner_id.id)
                if follower_ids:
                    picking.message_subscribe(partner_ids=follower_ids)
        return super(StockPicking, self).write(vals)

    @api.model
    def create(self, vals):
        if 'picking_type_id' in vals:
            picking_type_id = self.env['stock.picking.type'].search([('id', '=', vals['picking_type_id'])])
            if picking_type_id.name == 'Dropship':
                vals['purchasing_carrier_id'] = 8
                vals['crma_carrier_id'] = 0
            if picking_type_id.code != 'outgoing':
                vals['carrier_id'] = 0
        res = super(StockPicking, self).create(vals)
        if res.picking_type_id.code == 'incoming' and res.company_id.stock_followup_contact:
            follower_ids = []
            follower_ids.append(res.company_id.stock_followup_contact.partner_id.id)
            if res.owner_id:
                follower_ids.append(res.owner_id.id)
            if follower_ids:
                res.message_subscribe(partner_ids=follower_ids)
        return res

    #assign the carrier id for the treeview
    @api.model
    def _compute_carrier_tree(self):
        for rec in self:
            if rec.carrier_id:
                rec.carrier_id_tree_view = rec.carrier_id
            elif rec.po_carrier_id:
                rec.carrier_id_tree_view = rec.po_carrier_id
            elif rec.crma_carrier_id:
                rec.carrier_id_tree_view = rec.crma_carrier_id


    carrier_id_tree_view = fields.Many2one('delivery.carrier', compute='_compute_carrier_tree')

    # Reset the state_change_date everytime the state is changed.
    @api.depends('state')
    def set_change_date(self):
        for rec in self:
            if not rec.state_change_date:
                rec.state_change_date = datetime.now()
        return True

    #create a method to mark a stock picking as damaged
    @api.multi
    def action_damage(self):
        self.mapped('move_lines').filtered(lambda move: move.state == 'draft')._action_confirm()
        self.write({'state': 'damaged'})
        return True

    @api.multi
    def followup_reserve(self):
        self.action_assign()
        self.write({'state': 'assigned'})
        return True

    #check to see if the status needs to be changed to Followup Needed
    @api.model
    def _check_state_change_date(self):
        #get the records from the stock_picking table
        stock_pickings = self.env['stock.picking'].search([('picking_type_code', '=', 'incoming')])
        # Get current datetime stamp
        datetime_now = datetime.now()
        #Get the value in days for when a follow up is Needed
        config = self.env['res.config.settings'].get_values()
        followup = config['stock_followup_timeframe']
        #cycle through all inocming records on the stock_picking table
        for pick in stock_pickings:
            #check state, if state is in draft, damaged, or a "done" state, skip.
            if pick.state not in ('done', 'cancel', 'damaged', 'draft'):
                #format datetime_now and move.state_change_date to do the math.
                time_since_state_change = datetime_now - pick.state_change_date
                #compare time difference to preset stock_followup_timeframe
                if time_since_state_change.days > followup:
                    #check if state is in followup
                    if pick.state == 'followup':
                        #send email
                        pick.send_email_followup()
                        pick.state_change_date = datetime.now()
                    else:
                        #if a followup is required set to followup
                        pick.set_followup()
        return True


	#Button fuction to set state to follow up
    def set_followup(self):
        for rec in self:
            if rec.picking_type_code == 'incoming':
                rec.send_email_followup()
                rec.action_confirm()
                rec.write({'state': 'followup'})
        return True

    #create and send email to user in settigns
    @api.model
    def send_email_followup(self):
        partner = self.company_id.stock_followup_contact.partner_id
        if partner:
            message = "%s please follow up on %s" % (partner.name, self.name)
            self.sudo().message_post(body=message, message_type='notification', partner_ids=[partner.id])
        return True
