{
    "name": "InsightPulse Workspace Core",
    "summary": "Notion-style workspaces for organizing clients, brands, projects, campaigns",
    "version": "18.0.1.0.0",
    "category": "Productivity",
    "license": "LGPL-3",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "depends": [
        "base",
        "web",
        "mail",
        "contacts",
        "project",
    ],
    "data": [
        "security/workspace_security.xml",
        "security/ir.model.access.csv",
        "views/ipai_workspace_views.xml",
        "views/ipai_workspace_menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # keep empty for now – no JS/CSS needed
        ],
    },
    "installable": True,
    "application": False,  # app icon controlled by menu web_icon
}
