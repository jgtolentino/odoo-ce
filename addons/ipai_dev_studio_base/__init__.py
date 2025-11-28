# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Post-installation hook to configure CE-only environment."""
    _logger.info('[IPAI Dev Studio Base] Running post_init_hook...')

    # Disable IAP services
    iap_param = env['ir.config_parameter'].sudo()
    iap_param.set_param('iap.disabled', 'True')
    _logger.info('[IPAI Dev Studio Base] IAP disabled: iap.disabled=True')

    # Set InsightPulse branding parameters
    iap_param.set_param('ipai.edition', 'ce')
    iap_param.set_param('ipai.stack', 'odoo18-oca')

    _logger.info('[IPAI Dev Studio Base] Foundation module initialized successfully')
