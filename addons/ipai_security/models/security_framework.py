# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Security Framework Model
========================

Defines compliance frameworks that the organization tracks:
- PH Data Privacy Act (DPA)
- ISO 27001 (ISMS)
- SOC 2 Trust Service Criteria
- NIST AI Risk Management Framework
- ISO 42001 (AIMS)
"""
from odoo import api, fields, models


class SecurityFramework(models.Model):
    """
    Compliance framework definition.

    Each framework represents a regulatory or industry standard that the
    organization aligns with. Controls are mapped to one or more frameworks.

    Attributes:
        _name: Model technical name
        _description: Human-readable model description
        _order: Default ordering for lists
    """

    _name = "security.framework"
    _description = "Security Compliance Framework"
    _order = "sequence, name"

    name = fields.Char(
        string="Framework Name",
        required=True,
        help="Full name of the compliance framework (e.g., ISO 27001:2022)",
    )
    code = fields.Char(
        string="Code",
        required=True,
        help="Short code for the framework (e.g., ISO27001, SOC2, DPA)",
    )
    description = fields.Text(
        string="Description",
        help="Detailed description of the framework and its purpose",
    )
    category = fields.Selection(
        [
            ("data_privacy", "Data Privacy"),
            ("info_security", "Information Security"),
            ("trust_services", "Trust Services"),
            ("ai_governance", "AI Governance"),
            ("other", "Other"),
        ],
        string="Category",
        default="info_security",
        required=True,
        help="Classification of the framework type",
    )
    version = fields.Char(
        string="Version",
        help="Framework version (e.g., 2022, 2.0)",
    )
    issuing_body = fields.Char(
        string="Issuing Body",
        help="Organization that issues the framework (e.g., ISO, AICPA, NPC)",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        help="Whether this framework is currently in scope",
    )
    in_scope = fields.Boolean(
        string="In Scope for Certification",
        default=False,
        help="Whether the organization is pursuing certification for this framework",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Display order",
    )
    color = fields.Integer(
        string="Color Index",
        help="Color for kanban and dashboard display",
    )
    control_ids = fields.Many2many(
        "security.control",
        "security_control_framework_rel",
        "framework_id",
        "control_id",
        string="Controls",
        help="Controls mapped to this framework",
    )
    control_count = fields.Integer(
        string="Control Count",
        compute="_compute_control_count",
        store=True,
        help="Number of controls mapped to this framework",
    )
    coverage_percentage = fields.Float(
        string="Coverage %",
        compute="_compute_coverage",
        store=True,
        help="Percentage of controls with implemented status",
    )
    notes = fields.Html(
        string="Notes",
        help="Additional notes about framework implementation",
    )

    _sql_constraints = [
        (
            "code_unique",
            "UNIQUE(code)",
            "Framework code must be unique!",
        ),
    ]

    @api.depends("control_ids")
    def _compute_control_count(self):
        """Compute the number of controls mapped to this framework."""
        for framework in self:
            framework.control_count = len(framework.control_ids)

    @api.depends("control_ids", "control_ids.status")
    def _compute_coverage(self):
        """
        Compute framework coverage percentage.

        Coverage is calculated as the percentage of controls that have
        a status of 'implemented' or 'tested'.
        """
        for framework in self:
            if not framework.control_ids:
                framework.coverage_percentage = 0.0
            else:
                implemented = framework.control_ids.filtered(
                    lambda c: c.status in ("implemented", "tested")
                )
                framework.coverage_percentage = (
                    len(implemented) / len(framework.control_ids)
                ) * 100


class SecurityLawfulBasis(models.Model):
    """
    Lawful basis for data processing under PH DPA.

    This model defines the legal bases under which personal data can be
    processed according to the Philippines Data Privacy Act.
    """

    _name = "security.lawful.basis"
    _description = "Lawful Basis for Data Processing"
    _order = "sequence, name"

    name = fields.Char(
        string="Lawful Basis",
        required=True,
        help="Name of the lawful basis (e.g., Consent, Legitimate Interest)",
    )
    code = fields.Char(
        string="Code",
        required=True,
        help="Short code for reference",
    )
    description = fields.Text(
        string="Description",
        help="Detailed explanation of when this basis applies",
    )
    dpa_reference = fields.Char(
        string="DPA Reference",
        help="Section reference in the PH Data Privacy Act",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    _sql_constraints = [
        (
            "code_unique",
            "UNIQUE(code)",
            "Lawful basis code must be unique!",
        ),
    ]
