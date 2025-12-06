# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Security & Compliance Workbench
===============================

This module provides comprehensive security governance for the Fin Workspace,
aligned with PH DPA, ISO 27001, SOC 2, and AI governance frameworks.

Models
------
* security.asset - Asset inventory (apps, agents, droplets, databases)
* security.risk - Risk register with severity and likelihood tracking
* security.control - Controls matrix mapped to compliance frameworks
* security.data.flow - Data flow mapping for PH DPA compliance
* security.data.category - Data category definitions
* ai.system - AI systems register with NIST AI RMF alignment
* security.incident - Security incident tracking
* security.audit - Audit and assessment management
* security.framework - Compliance framework definitions

Controllers
-----------
* SecurityAPIController - JSON REST API for agents and automation
"""
from . import models
from . import controllers
from . import wizards
