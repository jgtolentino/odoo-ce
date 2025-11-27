# -*- coding: utf-8 -*-
{
    "name": "IPAI Workspace Core",
    "summary": "Notion-style business workspace browser for clients, brands, and campaigns",
    "description": """
IPAI Workspace Core
===================

A unified workspace layer for managing:
- Accounting clients
- Marketing brands
- Marketing campaigns
- Generic workspaces

Features:
- Notion-style clean UI with minimal chrome
- Table/Board/Calendar views
- Saved views and filters
- Status tracking (Active, Onboarding, At Risk, Closed)
- Owner/member management
    """,
    "version": "18.0.1.0.0",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "category": "Productivity",
    "depends": ["base", "mail", "contacts"],
    "data": [
        "security/ir.model.access.csv",
        "views/workspace_views.xml",
        "views/assets.xml",
        "views/menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_workspace_core/static/src/css/notion_style.css",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
