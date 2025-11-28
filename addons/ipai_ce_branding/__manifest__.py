# -*- coding: utf-8 -*-
{
    "name": "IPAI CE Branding",
    "summary": "InsightPulse CE/OCA branding: removes Odoo upsells and applies custom theme",
    "description": """
IPAI CE Branding - Community Edition Compliance
===============================================

Ensures the Odoo stack remains CE/OCA compliant by:
- Removing Odoo Enterprise branding and upsell prompts
- Disabling IAP services
- Hiding upgrade banners and odoo.com links
- Applying InsightPulse branded styling
- Customizing the login page

OCA Layer Integration:
---------------------
- portal_odoo_debranding: Removes Odoo branding from portal
- theme_cobalt: Professional corporate theme

Custom Delta:
------------
- InsightPulse/TBWA logos and color palette
- Custom login page styling
- Additional CSS overrides

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
    "version": "18.0.4.0.0",
    "category": "Hidden",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "portal",
        "website",
        "ipai_dev_studio_base",        # Foundation (Canonical 1 of 5)
        "portal_odoo_debranding",      # OCA server-brand debranding
        "theme_cobalt",                # OCA corporate theme
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
