{
    "name": "Remove Odoo Branding from Portal",
    "version": "18.0.1.0.0",
    "category": "Hidden",
    "summary": "Remove Odoo branding from portal pages",
    "description": """
Portal Odoo Debranding
======================

Removes Odoo branding elements from portal pages:
- Footer Odoo links
- "Powered by Odoo" text
- odoo.com references

Part of OCA server-brand repository.

Note: This is a placeholder structure. Replace with actual OCA portal_odoo_debranding content.
    """,
    "author": "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-brand",
    "license": "LGPL-3",
    "depends": [
        "portal",
    ],
    "data": [
        "views/portal_templates.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
