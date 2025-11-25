# -*- coding: utf-8 -*-
{
    "name": "IPAI Workspace Core",
    "summary": "Notion-style workspaces with pages, blocks, and collaborative editing",
    "description": """
IPAI Workspace Core
===================

A Notion-inspired workspace module for Odoo CE that provides:

* **Workspaces**: Collaborative containers with privacy controls
* **Pages**: Hierarchical documents with rich content
* **Blocks**: Modular content units (text, headings, todos, embeds)
* **Backlinks**: Bi-directional page references
* **Templates**: Reusable page structures

Part of the IPAI Productivity Suite.
    """,
    "version": "18.0.1.0.0",
    "category": "Productivity/Workspace",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "web",
    ],
    "data": [
        # Security - must be loaded first
        "security/workspace_security.xml",
        "security/ir.model.access.csv",
        # Data
        "data/workspace_data.xml",
        # Views
        "views/workspace_views.xml",
        "views/page_views.xml",
        "views/block_views.xml",
        "views/template_views.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_workspace_core/static/src/css/workspace.css",
            "ipai_workspace_core/static/src/js/block_editor.js",
        ],
    },
    "demo": [
        "demo/workspace_demo.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "sequence": 10,
}
