from odoo import models

class ThemeLaze(models.AbstractModel):
    _inherit = 'theme.utils'

    def _theme_laze_post_copy(self, mod):
        self.disable_view('website_theme_install.customize_modal')
