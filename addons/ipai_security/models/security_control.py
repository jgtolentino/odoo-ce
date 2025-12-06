# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Security Control Model
======================

Controls matrix for compliance framework mapping.
Supports mapping to:
- ISO 27001:2022 controls
- SOC 2 Trust Service Criteria
- PH Data Privacy Act requirements
- NIST AI RMF measures
- ISO 42001 AIMS controls
"""
from odoo import api, fields, models


class SecurityControl(models.Model):
    """
    Security control definition.

    Each control represents a safeguard or countermeasure that addresses
    one or more security risks and supports compliance objectives.

    Attributes:
        _name: Model technical name
        _description: Human-readable model description
        _inherit: Parent models for audit trail
        _order: Default ordering
    """

    _name = "security.control"
    _description = "Security Control"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "framework_id, code"

    name = fields.Char(
        string="Control Title",
        required=True,
        tracking=True,
        help="Title of the security control",
    )
    code = fields.Char(
        string="Control Code",
        required=True,
        tracking=True,
        help="Control identifier (e.g., A.5.1.1, CC1.1)",
    )
    description = fields.Text(
        string="Description",
        required=True,
        help="Detailed description of the control requirements",
    )
    implementation_guidance = fields.Text(
        string="Implementation Guidance",
        help="Guidance on how to implement this control",
    )
    # Framework mapping
    framework_id = fields.Many2one(
        "security.framework",
        string="Primary Framework",
        required=True,
        tracking=True,
        help="Primary framework this control belongs to",
    )
    framework_ids = fields.Many2many(
        "security.control",
        "security_control_framework_rel",
        "control_id",
        "framework_id",
        string="All Frameworks",
        help="All frameworks this control maps to",
    )
    # SOC 2 specific
    soc2_category = fields.Selection(
        [
            ("security", "Security"),
            ("availability", "Availability"),
            ("processing_integrity", "Processing Integrity"),
            ("confidentiality", "Confidentiality"),
            ("privacy", "Privacy"),
        ],
        string="SOC 2 Category",
        help="SOC 2 Trust Service Category (if applicable)",
    )
    # Control classification
    control_type = fields.Selection(
        [
            ("preventive", "Preventive"),
            ("detective", "Detective"),
            ("corrective", "Corrective"),
            ("compensating", "Compensating"),
        ],
        string="Control Type",
        default="preventive",
        help="Type of control based on its function",
    )
    control_nature = fields.Selection(
        [
            ("technical", "Technical"),
            ("administrative", "Administrative"),
            ("physical", "Physical"),
        ],
        string="Control Nature",
        default="technical",
        help="Nature of the control implementation",
    )
    automation_level = fields.Selection(
        [
            ("manual", "Manual"),
            ("semi_automated", "Semi-Automated"),
            ("automated", "Fully Automated"),
        ],
        string="Automation Level",
        default="manual",
        help="Level of automation in control execution",
    )
    # Implementation status
    status = fields.Selection(
        [
            ("not_implemented", "Not Implemented"),
            ("partially_implemented", "Partially Implemented"),
            ("implemented", "Implemented"),
            ("tested", "Tested & Verified"),
            ("not_applicable", "Not Applicable"),
        ],
        string="Status",
        default="not_implemented",
        required=True,
        tracking=True,
        help="Current implementation status",
    )
    implementation_date = fields.Date(
        string="Implementation Date",
        tracking=True,
        help="Date when control was implemented",
    )
    # Testing and evidence
    test_frequency = fields.Selection(
        [
            ("continuous", "Continuous"),
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annually", "Annually"),
            ("ad_hoc", "Ad-Hoc"),
        ],
        string="Test Frequency",
        default="quarterly",
        help="How often this control should be tested",
    )
    last_test_date = fields.Date(
        string="Last Test Date",
        tracking=True,
        help="Date of last control test",
    )
    next_test_date = fields.Date(
        string="Next Test Date",
        help="Scheduled date for next test",
    )
    test_result = fields.Selection(
        [
            ("passed", "Passed"),
            ("failed", "Failed"),
            ("partial", "Partial Pass"),
            ("not_tested", "Not Tested"),
        ],
        string="Last Test Result",
        default="not_tested",
        tracking=True,
        help="Result of the last control test",
    )
    evidence_url = fields.Char(
        string="Evidence URL",
        help="Link to evidence documentation (e.g., GitHub, Confluence)",
    )
    evidence_description = fields.Text(
        string="Evidence Description",
        help="Description of evidence that supports control implementation",
    )
    # Ownership
    owner_id = fields.Many2one(
        "res.users",
        string="Control Owner",
        tracking=True,
        help="User responsible for this control",
    )
    owner_role = fields.Selection(
        [
            ("security_officer", "Security Officer"),
            ("engineer", "Engineer"),
            ("ai_lead", "AI Lead"),
            ("owner", "Owner"),
        ],
        string="Owner Role",
        help="Role responsible for the control",
    )
    # Asset and risk linkages
    asset_ids = fields.Many2many(
        "security.asset",
        "security_asset_control_rel",
        "control_id",
        "asset_id",
        string="Applied To Assets",
        help="Assets this control is applied to",
    )
    asset_count = fields.Integer(
        string="Asset Count",
        compute="_compute_asset_count",
        store=True,
    )
    risk_ids = fields.Many2many(
        "security.risk",
        "security_risk_control_rel",
        "control_id",
        "risk_id",
        string="Mitigated Risks",
        help="Risks this control mitigates",
    )
    risk_count = fields.Integer(
        string="Risk Count",
        compute="_compute_risk_count",
        store=True,
    )
    # Priority and organization
    priority = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Priority",
        default="medium",
        help="Implementation priority",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    color = fields.Integer(
        string="Color Index",
        compute="_compute_color",
        store=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    notes = fields.Html(
        string="Notes",
        help="Additional notes and implementation details",
    )

    _sql_constraints = [
        (
            "code_framework_unique",
            "UNIQUE(code, framework_id)",
            "Control code must be unique within a framework!",
        ),
    ]

    @api.depends("asset_ids")
    def _compute_asset_count(self):
        """Count assets this control applies to."""
        for control in self:
            control.asset_count = len(control.asset_ids)

    @api.depends("risk_ids")
    def _compute_risk_count(self):
        """Count risks this control mitigates."""
        for control in self:
            control.risk_count = len(control.risk_ids)

    @api.depends("status")
    def _compute_color(self):
        """Set color based on implementation status."""
        color_map = {
            "not_implemented": 1,  # Red
            "partially_implemented": 3,  # Yellow
            "implemented": 10,  # Green
            "tested": 11,  # Light green
            "not_applicable": 0,  # Gray
        }
        for control in self:
            control.color = color_map.get(control.status, 0)

    @api.onchange("test_frequency", "last_test_date")
    def _onchange_test_dates(self):
        """Calculate next test date based on frequency."""
        if self.last_test_date and self.test_frequency:
            from dateutil.relativedelta import relativedelta

            freq_delta = {
                "daily": relativedelta(days=1),
                "weekly": relativedelta(weeks=1),
                "monthly": relativedelta(months=1),
                "quarterly": relativedelta(months=3),
                "annually": relativedelta(years=1),
            }
            delta = freq_delta.get(self.test_frequency)
            if delta:
                self.next_test_date = self.last_test_date + delta

    def action_mark_implemented(self):
        """Mark control as implemented."""
        self.ensure_one()
        self.write({
            "status": "implemented",
            "implementation_date": fields.Date.today(),
        })

    def action_mark_tested(self):
        """Mark control as tested and passed."""
        self.ensure_one()
        self.write({
            "status": "tested",
            "last_test_date": fields.Date.today(),
            "test_result": "passed",
        })

    def action_view_assets(self):
        """Open related assets view."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Assets: {self.name}",
            "res_model": "security.asset",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.asset_ids.ids)],
        }

    def action_view_risks(self):
        """Open related risks view."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Risks: {self.name}",
            "res_model": "security.risk",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.risk_ids.ids)],
        }
