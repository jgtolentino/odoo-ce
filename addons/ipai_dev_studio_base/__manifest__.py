# -*- coding: utf-8 -*-
{
    'name': 'IPAI Dev Studio Base',
    'version': '18.0.1.0.0',
    'category': 'Technical',
    'summary': 'Foundation module - aggregates CE/OCA dependencies, disables IAP',
    'description': """
IPAI Dev Studio Base - Foundation Module
========================================

This is the MANDATORY foundation module for all InsightPulse ERP deployments.
All other ipai_* modules MUST depend on this module.

Purpose:
--------
1. Aggregates all necessary CE and OCA module dependencies
2. Disables IAP (In-App Purchase) to ensure CE-only operation
3. Sets system parameters for CE compliance
4. Provides base configuration for AI agent development

Smart Delta Philosophy:
----------------------
Config -> OCA -> Delta -> Custom

This module ensures the stack is properly configured before any
custom modules are installed.

Canonical Module: 1 of 5
Part of InsightPulse ERP Target Image

Dependencies Aggregated:
-----------------------
* base, mail, project (CE core)
* web, contacts, calendar (CE apps)
* OCA web modules (when available)

Author: InsightPulse AI
License: AGPL-3
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',
    'depends': [
        # CE Core
        'base',
        'mail',
        'web',
        # CE Apps (commonly needed)
        'contacts',
        'calendar',
        'project',
        'account',
        'resource',
    ],
    'data': [
        'data/iap_disable.xml',
        'data/system_parameters.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}
