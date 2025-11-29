{
    "name": "IPAI Web Home - App Grid at /odoo",
    "summary": "Override /odoo route to show app grid menu instead of discuss redirect",
    "version": "18.0.1.0.0",
    "author": "InsightPulse AI",
    "license": "AGPL-3",
    "website": "https://insightpulseai.net",
    "category": "Web",
    "depends": ["web"],
    "data": [],
    "assets": {
        "web.assets_backend": [
            "ipai_web_home/static/src/js/web_client.js",
        ],
    },
    "application": False,
    "installable": True,
}
