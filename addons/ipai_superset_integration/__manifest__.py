{
    "name": "IPAI Superset Integration",
    "summary": "Apache Superset dashboard links in Odoo menu",
    "version": "18.0.1.0.0",
    "author": "InsightPulse AI",
    "license": "AGPL-3",
    "website": "https://insightpulseai.net",
    "category": "Reporting",
    "depends": ["web"],
    "data": [
        "data/superset_actions.xml",
        "views/superset_menus.xml",
    ],
    "application": False,
    "installable": True,
}
