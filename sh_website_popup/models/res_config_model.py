# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.


from odoo import api, fields, models

class WebisteConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'

    swp_is_popup_msg = fields.Boolean(related='website_id.swp_is_popup_msg',string="swp popup Message", readonly = False)
    swp_titile = fields.Char(related="website_id.swp_titile", string="popup Title", readonly = False)
    swp_add_message = fields.Boolean(related="website_id.swp_add_message", string="Add Message", readonly = False)
    swp_message = fields.Html(related="website_id.swp_message",string="popup Message", readonly = False)
    swp_dismiss_btn_name = fields.Char(related="website_id.swp_dismiss_btn_name", readonly = False)
    swp_link_btn_name = fields.Char(related="website_id.swp_link_btn_name", string="popup Link Button Name", readonly = False)
    swp_link_url = fields.Char(related="website_id.swp_link_url", string = "popup Link URL", readonly = False)
    swp_banner_img = fields.Binary(related="website_id.swp_banner_img", string="popup Image", readonly = False)
#    swp_banner_img_sm = fields.Binary(related="website_id.swp_banner_img_sm", string="Small Screen Image", readonly = False)


class website(models.Model):
    _inherit = 'website'

    swp_is_popup_msg = fields.Boolean(string="swp popup Message")
    swp_titile = fields.Char(string="popup Title")
    swp_add_message = fields.Boolean(string="Add Message")
    swp_message = fields.Html(string="popup Message")
    swp_dismiss_btn_name =fields.Char(string="Dismiss Button Name")
    swp_link_btn_name = fields.Char(string="popup Link Button Name")
    swp_link_url = fields.Char(string = "popup Link URL")
    swp_banner_img = fields.Binary(string="popup Image")
#    swp_banner_img_sm = fields.Binary(string="Small Screen Image")
