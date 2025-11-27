# -*- coding: utf-8 -*-
{
    "name": "Finance Workflow (RACI + Stages)",
    "summary": "Finance workflow stages, RACI-aware tasks, checklist for month-end/BIR/PPM",
    "version": "18.0.1.0.0",
    "author": "InsightPulseAI",
    "license": "LGPL-3",
    "category": "Finance",
    "depends": [
        "base",
        "mail",
        "project",
        "ipai_person",
        "ipai_workspace_core",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ipai_finance_stage_seed.xml",
        "views/ipai_finance_stage_views.xml",
        "views/ipai_finance_task_views.xml",
        "views/ipai_task_checklist_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
