# -*- coding: utf-8 -*-
{
    "name": "IPAI CE Cleaner - InsightPulse Branding",
    "summary": "Removes Odoo branding, disables IAP, and applies InsightPulse branding.",
    "description": """
InsightPulse ERP Branding Module
================================

This module:
- Removes all Odoo branding (logo, favicon, page title)
- Disables IAP services and Enterprise upsells
- Hides upgrade prompts and odoo.com links
- Applies InsightPulse branded styling
- Customizes the login page

Automatically configures:
- iap.disabled = True
- Clears database.enterprise_code
- Clears publisher_warranty.warranty_url
    """,
    "version": "18.0.2.0.0",
    "category": "Tools",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "web",
    ],
    "data": [
        "views/ipai_ce_cleaner_views.xml",
        "views/login_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_ce_cleaner/static/src/css/ipai_ce_cleaner.css",
            "ipai_ce_cleaner/static/src/js/branding.js",
        ],
        "web.assets_frontend": [
            "ipai_ce_cleaner/static/src/css/ipai_ce_cleaner.css",
        ],
    },
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
