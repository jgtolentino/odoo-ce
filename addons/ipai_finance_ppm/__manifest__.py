# -*- coding: utf-8 -*-
{
    "name": "IPAI Finance PPM",
    "summary": "Finance Project Portfolio Management - Accounting Industry Pack (Consolidated).",
    "description": """
Finance PPM - Accounting Industry Pack
======================================

Consolidated module combining:
- ipai_finance_ppm (BIR deadline tracking, team directory)
- ipai_finance_ppm_dashboard (ECharts dashboard)
- ipai_finance_monthly_closing (Month-end structured closing)
- ipai_ppm_monthly_close (Recurring close scheduler)

Features:
---------
* BIR Tax Filing Calendar (22 deadlines for 2026)
* Month-end Close Workflow (Owner → Reviewer → Approver)
* Finance Team Directory with contact info
* SOP Document Templates for BIR forms
* Automated deadline alerts (7-day, 3-day, 1-day, overdue)
* Activity scheduling and @mention notifications
* ECharts dashboard visualization
* Clarity PPM hierarchy (Phase → Task → To-Do → Milestone)

CE Module Dependencies:
----------------------
* account - Core accounting
* resource - Business day calculations

Canonical Module: 4 of 5
Part of InsightPulse ERP Target Image (Smart Delta Philosophy)

Author: InsightPulse AI
License: AGPL-3
    """,
    "version": "18.0.3.0.0",
    "category": "Accounting/Finance",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "ipai_dev_studio_base",  # Foundation module (Canonical 1 of 5)
        "mail",
        "project",
        "resource",  # Business day calculations
        "account",   # Core accounting CE
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/finance_person_views.xml",
        "views/finance_bir_deadline_views.xml",
        "views/finance_sop_views.xml",
        "views/finance_task_views.xml",
        "views/finance_phase_views.xml",
        "views/bir_schedule_views.xml",
        "views/ppm_dashboard_views.xml",
        "views/project_task_views.xml",
        "views/menus.xml",
        "data/finance_person_seed.xml",
        "data/finance_bir_deadline_2026.xml",
        "data/finance_task_template_seed.xml",
        "data/bir_schedule_seed.xml",
        "data/finance_cron.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_finance_ppm/static/src/js/semantic-search/api.js",
            "ipai_finance_ppm/static/src/js/semantic-search/MonthlyRevenueSearch.js",
            "ipai_finance_ppm/static/src/xml/monthly_revenue_search.xml",
            # Dashboard ECharts assets
            "ipai_finance_ppm/static/lib/echarts.min.js",
            "ipai_finance_ppm/static/src/js/ppm_dashboard.js",
            "ipai_finance_ppm/static/src/xml/ppm_dashboard_templates.xml",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
