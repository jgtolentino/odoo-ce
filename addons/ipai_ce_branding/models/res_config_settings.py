# -*- coding: utf-8 -*-
from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def _disable_iap_and_enterprise(self):
        """Disable IAP services and clear Enterprise references.

        Called on module installation to ensure clean CE environment.
        """
        ICP = self.env['ir.config_parameter'].sudo()

        # Disable IAP
        ICP.set_param('iap.disabled', 'True')

        # Clear Enterprise code references
        ICP.set_param('database.enterprise_code', '')
        ICP.set_param('publisher_warranty.warranty_url', '')

        # Disable Odoo.com push notifications
        ICP.set_param('odoo_ocn.project_id', '')

        # Set custom branding parameters
        ICP.set_param('web.base.url.freeze', 'True')

        _logger.info("IPAI CE Cleaner: Disabled IAP and cleared Enterprise references")

        return True
