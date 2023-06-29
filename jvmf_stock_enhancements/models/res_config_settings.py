# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta



class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Create, setup, and retrieve the information for the number of days till a followup is required and the person who needs to be notified.
    stock_followup_timeframe = fields.Integer('Days till Followup', default_model='stock.picking',
        help='The number of days since the last state change before a followup is required')
    stock_followup_contact = fields.Many2one('res.users', string='Stock Followup Contact', domain=[('share', '=', False)], related='company_id.stock_followup_contact', readonly=False,
        help='The person who needs to receive the followup notification.')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res['stock_followup_timeframe'] = float(self.env['ir.config_parameter'].sudo().get_param('followup.stock_followup_timeframe', default=13.0))
        return res


    @api.multi
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('followup.stock_followup_timeframe', self.stock_followup_timeframe)
        super(ResConfigSettings, self).set_values()
