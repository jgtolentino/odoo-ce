# -*- coding: utf-8 -*-
{
    "name": "IPAI CE Branding",
    "summary": "CE/OCA branding - removes Enterprise upsells, applies InsightPulse styling.",
    "description": """
IPAI CE Branding - Community Edition Compliance
===============================================

Ensures the Odoo stack remains CE/OCA compliant by:
- Removing Odoo Enterprise branding and upsell prompts
- Disabling IAP services
- Hiding upgrade banners and odoo.com links
- Applying InsightPulse branded styling
- Customizing the login page

Configuration Applied:
---------------------
- iap.disabled = True
- Clears database.enterprise_code
- Clears publisher_warranty.warranty_url

Canonical Module: 3 of 5
Part of InsightPulse ERP Target Image (Smart Delta Philosophy)

Author: InsightPulse AI
License: AGPL-3
    """,
    "version": "18.0.3.0.0",
    "category": "Tools",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "ipai_dev_studio_base",  # Foundation dependency
        "web",
    ],
    "data": [
        "views/ipai_ce_branding_views.xml",
        "views/login_templates.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_ce_branding/static/src/css/ipai_ce_branding.css",
            "ipai_ce_branding/static/src/js/branding.js",
        ],
        "web.assets_frontend": [
            "ipai_ce_branding/static/src/css/ipai_ce_branding.css",
        ],
    },
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
