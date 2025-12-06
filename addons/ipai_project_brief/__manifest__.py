# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
{
    "name": "IPAI Project Brief",
    "summary": "Structured project briefs for creative/agency projects",
    "description": """
IPAI Project Brief
==================

This module adds a structured "Project Brief" object to Odoo 18 CE,
designed for creative and agency workflows.

Features
--------
* New model: project.brief with title, client, brand, objectives
* Status flow: Draft -> In Review -> Approved / On Hold / Cancelled
* Automatic lock of approved briefs (non-admin users cannot edit)
* Menu and views under Project module
* Demo data for quick testing
* Basic test coverage

Dependencies
------------
* Project
* Contacts
    """,
    "version": "18.0.1.0.0",
    "category": "Project",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": [
        "project",
        "contacts",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/project_menu.xml",
        "views/project_brief_views.xml",
        "data/project_brief_demo.xml",
    ],
    "demo": [
        "data/project_brief_demo.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
