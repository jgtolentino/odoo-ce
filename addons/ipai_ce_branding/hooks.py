# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Post-installation hook to disable IAP and Enterprise features."""
    _logger.info("IPAI CE Cleaner: Running post-install configuration...")

    ICP = env['ir.config_parameter'].sudo()

    # Disable IAP services
    ICP.set_param('iap.disabled', 'True')

    # Clear Enterprise-related parameters
    ICP.set_param('database.enterprise_code', '')
    ICP.set_param('publisher_warranty.warranty_url', '')

    # Disable Odoo Cloud Notifications
    ICP.set_param('odoo_ocn.project_id', '')

    # Prevent accidental odoo.com connections
    ICP.set_param('web.base.url.freeze', 'True')

    _logger.info("IPAI CE Cleaner: IAP disabled, Enterprise references cleared")


def uninstall_hook(env):
    """Cleanup on module uninstall."""
    _logger.info("IPAI CE Cleaner: Module uninstalled, settings remain for safety")
