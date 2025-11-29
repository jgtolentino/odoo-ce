{
    "name": "IPAI Keycloak SSO",
    "summary": "Single Sign-On via Keycloak for Odoo CE 18.0",
    "version": "18.0.1.0.0",
    "author": "InsightPulse AI",
    "license": "AGPL-3",
    "website": "https://insightpulseai.net",
    "category": "Authentication",
    "depends": ["auth_oauth"],
    "data": [
        "data/auth_oauth_data.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}
