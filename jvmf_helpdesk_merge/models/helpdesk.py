# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api
from odoo.addons.helpdesk.models.helpdesk_ticket import HelpdeskTicket as super_ticket


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    is_merge = fields.Boolean('Merge', default=False, copy=False)
    merged_ids = fields.Many2many('helpdesk.ticket',
                                  'helpdesk_ticket_merge_ticket_rel',
                                  'helpdesk_id',
                                  'merge_ticket_id',
                                  string='Merged Tickets', copy=False)
    merge_checked = fields.Boolean('Merge ticket', related='team_id.merge_ticket')

    parent_id = fields.Many2one('helpdesk.ticket', string='Master Task')
    child_ids = fields.One2many('helpdesk.ticket','parent_id', domain=['|', ('active', '=', False), ('active', '=', True)])

    def _merged_count(self):
        for ticket in self:
            ticket.merged_count = len(ticket.child_ids)

    merged_count = fields.Integer(compute='_merged_count', string='Number of Merged Tickets')

    @api.multi
    def _track_template(self, tracking):
        if self._context.get('merge_ticket'):
            return super(super_ticket, self)._track_template(tracking)
        else:
            return super(HelpdeskTicket, self)._track_template(tracking)

    @api.depends('partner_id')
    def _compute_partner_tickets(self):
        for ticket in self:
            ticket_data = self.env['helpdesk.ticket'].read_group([
                ('partner_id', '=', ticket.partner_id.id),
                ('stage_id.is_close', '=', False)
            ], ['partner_id'], ['partner_id'])
            if ticket_data:
                ticket.partner_tickets = ticket_data[0]['partner_id_count']


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    merge_ticket = fields.Boolean('Merge Ticket')
    communication = fields.Selection([('do_nothing',
                                       'Do Not Copy Communication'),
                                      ('copy_all_communication',
                                       'Copy All Communication')],
                                     default='do_nothing',
                                     required=True)
    email = fields.Selection([('do_not_send_mail', 'Do not send Mail'),
                              ('send_mail', 'Send Mail')],
                             default='do_not_send_mail',
                             required=True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
