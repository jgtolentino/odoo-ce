# -*- coding: utf-8 -*-
{
    'name': 'IPAI Industry - Marketing Agency',
    'version': '18.0.1.0.0',
    'category': 'Marketing',
    'summary': 'Marketing Agency Industry Pack - Brands, Campaigns, Budgets',
    'description': """
IPAI Industry - Marketing Agency Pack
=====================================

Extends ipai.workspace for marketing agency operations including:
- Brand management
- Campaign tracking
- Budget allocation and tracking
- Client project management
- Creative asset workflow

Features:
---------
* Brand registry with client associations
* Campaign lifecycle management (Planning → Active → Complete)
* Budget tracking per campaign/brand
* Creative brief templates
* Approval workflows for deliverables
* Integration with tbwa_spectra_integration (when installed)

Inherits From:
-------------
* ipai_workspace_core - Notion-style workspace foundation

Canonical Module: 5 of 5
Part of InsightPulse ERP Target Image (Smart Delta Philosophy)

Author: InsightPulse AI
License: AGPL-3
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',
    'depends': [
        'ipai_dev_studio_base',  # Foundation module (Canonical 1 of 5)
        'ipai_workspace_core',   # Workspace foundation (Canonical 2 of 5)
        'sale_management',       # For client/brand relationships
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/marketing_brand_views.xml',
        'views/marketing_campaign_views.xml',
        'views/marketing_menus.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
