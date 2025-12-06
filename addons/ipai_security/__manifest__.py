# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Security & Compliance Workbench",
    "summary": "Comprehensive security governance aligned with PH DPA, ISO 27001, SOC 2, and AI RMF",
    "description": """
Security & Compliance Workbench
===============================

A comprehensive security and compliance management system for the Fin Workspace.

Key Features
------------
* **Asset Inventory**: Track and classify all production assets (apps, agents,
  droplets, databases, buckets)
* **Risk Register**: Capture, rank, and track resolution of security risks
* **Controls Matrix**: Map controls to ISO 27001, SOC 2, PH DPA, and AI governance
  frameworks
* **AI Systems Register**: Catalogue AI systems with risk assessment and evaluation
  tracking (NIST AI RMF, ISO 42001)
* **Data Flow Mapping**: PH Data Privacy Act compliance with data categories and
  lawful basis tracking
* **Incidents & Audits**: Track security incidents and audit findings
* **KPI Dashboard**: Real-time security posture overview with framework coverage

Compliance Frameworks
---------------------
* Philippines Data Privacy Act (DPA) - NPC alignment
* ISO 27001 Information Security Management System (ISMS)
* SOC 2 Trust Service Criteria (Security, Availability, Confidentiality)
* NIST AI Risk Management Framework (AI RMF)
* ISO 42001 AI Management System (AIMS)

User Roles
----------
* **Owner**: Full access, manage frameworks and roles
* **Security Officer**: DPO/ISO lead, manage assets, risks, controls, audits
* **AI Lead**: AI governance, manage AI systems and evaluations
* **Engineer**: Technical access to assets and incidents
* **Auditor**: Read-only external review access

Technical Details
-----------------
This module integrates with the broader InsightPulseAI ecosystem and supports
agent-queryable security state for risk-aware AI operations.
    """,
    "version": "18.0.1.0.0",
    "category": "Security/Compliance",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "web",
    ],
    "data": [
        # Security (load first)
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        "security/security_rules.xml",
        # Data
        "data/framework_data.xml",
        "data/data_category_data.xml",
        "data/control_seed_data.xml",
        # Views
        "views/menu.xml",
        "views/security_asset_views.xml",
        "views/security_risk_views.xml",
        "views/security_control_views.xml",
        "views/security_data_flow_views.xml",
        "views/ai_system_views.xml",
        "views/security_incident_views.xml",
        "views/security_audit_views.xml",
        "views/dashboard_views.xml",
        # Wizards
        "wizards/asset_import_wizard_views.xml",
        "wizards/report_export_wizard_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "ipai_security/static/src/css/security_dashboard.css",
            "ipai_security/static/src/js/security_dashboard.js",
            "ipai_security/static/src/xml/security_templates.xml",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
