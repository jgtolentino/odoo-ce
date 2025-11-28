# -*- coding: utf-8 -*-
{
    "name": "IPAI Finance PPM",
    "summary": "Finance Project Portfolio Management with Notion-style Canvas.",
    "description": """
IPAI Finance PPM
================

A comprehensive Finance Project Portfolio Management module providing
Notion-like task tracking and BIR compliance scheduling for Philippine
businesses running on Odoo 18 CE.

**Key Features:**

* **Directory Management** - Track finance team members, roles, and responsibilities
* **Monthly Task Templates** - Recurring monthly close tasks with status tracking
* **BIR Compliance Calendar** - Philippine tax filing deadlines and reminders
* **PPM Dashboard** - Visual overview of project portfolio status
* **Revenue Insights Search** - Natural language semantic search over monthly revenue data

**Technical Stack:**

* Odoo 18 Community Edition (OCA)
* PostgreSQL 15
* Supabase for semantic embeddings (optional)
* OpenAI text-embedding-3-small (optional)

Part of the InsightPulse ERP ecosystem following the Smart Delta Philosophy.
    """,
    "version": "18.0.1.0.0",
    "category": "Accounting/Finance",
    "author": "InsightPulseAI",
    "website": "https://github.com/jgtolentino/odoo-ce",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "project",
    ],
    "data": [
        # 1. Security (must be first)
        "security/ir.model.access.csv",
        # 2. Data Seeds (before views that reference them)
        "data/bir_schedule_seed.xml",
        # 3. Views (in dependency order)
        "views/finance_person_views.xml",
        "views/finance_task_views.xml",
        "views/bir_schedule_views.xml",
        "views/ppm_dashboard_views.xml",
        "views/project_task_views.xml",
        # 4. Menus (last, after all actions are defined)
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_finance_ppm/static/src/js/semantic-search/api.js",
            "ipai_finance_ppm/static/src/js/semantic-search/MonthlyRevenueSearch.js",
            "ipai_finance_ppm/static/src/xml/monthly_revenue_search.xml",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
