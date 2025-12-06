# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Security Risk Model
===================

Risk register for tracking and managing security risks.
Supports risk assessment with:
- Severity and likelihood ratings
- Framework tagging (ISO 27001, SOC 2, DPA, AI RMF)
- Control linkage
- Asset association
"""
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SecurityRisk(models.Model):
    """
    Security risk register record.

    Each risk represents an identified threat or vulnerability that
    could impact the organization's security posture.

    Attributes:
        _name: Model technical name
        _description: Human-readable model description
        _inherit: Parent models for audit trail
        _order: Default ordering (highest severity first)
    """

    _name = "security.risk"
    _description = "Security Risk"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "severity DESC, likelihood DESC, id DESC"

    name = fields.Char(
        string="Risk Title",
        required=True,
        tracking=True,
        help="Brief title describing the risk",
    )
    reference = fields.Char(
        string="Reference",
        readonly=True,
        copy=False,
        default="New",
        help="Unique risk reference number",
    )
    description = fields.Text(
        string="Description",
        required=True,
        help="Detailed description of the risk, its causes, and potential impacts",
    )
    risk_category = fields.Selection(
        [
            ("technical", "Technical"),
            ("operational", "Operational"),
            ("compliance", "Compliance"),
            ("strategic", "Strategic"),
            ("reputational", "Reputational"),
            ("financial", "Financial"),
            ("ai_specific", "AI-Specific"),
        ],
        string="Risk Category",
        default="technical",
        required=True,
        tracking=True,
        help="Category of risk for classification",
    )
    # Risk assessment
    severity = fields.Selection(
        [
            ("1_negligible", "Negligible"),
            ("2_minor", "Minor"),
            ("3_moderate", "Moderate"),
            ("4_major", "Major"),
            ("5_critical", "Critical"),
        ],
        string="Severity",
        default="3_moderate",
        required=True,
        tracking=True,
        help="Impact severity if the risk materializes",
    )
    likelihood = fields.Selection(
        [
            ("1_rare", "Rare"),
            ("2_unlikely", "Unlikely"),
            ("3_possible", "Possible"),
            ("4_likely", "Likely"),
            ("5_almost_certain", "Almost Certain"),
        ],
        string="Likelihood",
        default="3_possible",
        required=True,
        tracking=True,
        help="Probability of the risk occurring",
    )
    inherent_risk_score = fields.Integer(
        string="Inherent Risk Score",
        compute="_compute_risk_scores",
        store=True,
        help="Risk score before controls (severity x likelihood)",
    )
    residual_risk_score = fields.Integer(
        string="Residual Risk Score",
        compute="_compute_risk_scores",
        store=True,
        help="Risk score after controls",
    )
    risk_level = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Risk Level",
        compute="_compute_risk_scores",
        store=True,
        help="Overall risk level based on score",
    )
    # Status and treatment
    status = fields.Selection(
        [
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("mitigated", "Mitigated"),
            ("accepted", "Accepted"),
            ("transferred", "Transferred"),
            ("closed", "Closed"),
        ],
        string="Status",
        default="open",
        required=True,
        tracking=True,
        help="Current status of risk treatment",
    )
    treatment_strategy = fields.Selection(
        [
            ("mitigate", "Mitigate"),
            ("accept", "Accept"),
            ("transfer", "Transfer"),
            ("avoid", "Avoid"),
        ],
        string="Treatment Strategy",
        help="Chosen approach for handling this risk",
    )
    treatment_plan = fields.Text(
        string="Treatment Plan",
        help="Detailed plan for risk treatment",
    )
    # Framework associations
    framework_ids = fields.Many2many(
        "security.framework",
        "security_risk_framework_rel",
        "risk_id",
        "framework_id",
        string="Related Frameworks",
        help="Compliance frameworks this risk relates to",
    )
    # Asset and control linkages
    asset_ids = fields.Many2many(
        "security.asset",
        "security_asset_risk_rel",
        "risk_id",
        "asset_id",
        string="Affected Assets",
        help="Assets affected by this risk",
    )
    asset_count = fields.Integer(
        string="Asset Count",
        compute="_compute_asset_count",
        store=True,
    )
    control_ids = fields.Many2many(
        "security.control",
        "security_risk_control_rel",
        "risk_id",
        "control_id",
        string="Mitigating Controls",
        help="Controls that mitigate this risk",
    )
    control_count = fields.Integer(
        string="Control Count",
        compute="_compute_control_count",
        store=True,
    )
    control_effectiveness = fields.Float(
        string="Control Effectiveness %",
        compute="_compute_control_effectiveness",
        store=True,
        help="Percentage of mitigating controls that are implemented",
    )
    # AI-specific fields (for AI governance)
    is_ai_related = fields.Boolean(
        string="AI-Related Risk",
        default=False,
        help="Whether this risk is specific to AI systems",
    )
    ai_system_ids = fields.Many2many(
        "ai.system",
        "security_risk_ai_system_rel",
        "risk_id",
        "ai_system_id",
        string="Related AI Systems",
        help="AI systems this risk applies to",
    )
    ai_risk_type = fields.Selection(
        [
            ("bias", "Algorithmic Bias"),
            ("transparency", "Lack of Transparency"),
            ("privacy", "Privacy Violation"),
            ("safety", "Safety/Harm"),
            ("security", "Security Vulnerability"),
            ("accountability", "Accountability Gap"),
            ("performance", "Performance Degradation"),
            ("regulatory", "Regulatory Non-Compliance"),
        ],
        string="AI Risk Type",
        help="Specific type of AI-related risk",
    )
    # Ownership and dates
    owner_id = fields.Many2one(
        "res.users",
        string="Risk Owner",
        tracking=True,
        help="User responsible for managing this risk",
    )
    identified_date = fields.Date(
        string="Identified Date",
        default=fields.Date.today,
        required=True,
        help="Date when risk was identified",
    )
    target_resolution_date = fields.Date(
        string="Target Resolution Date",
        tracking=True,
        help="Target date for risk resolution",
    )
    actual_resolution_date = fields.Date(
        string="Actual Resolution Date",
        tracking=True,
        help="Date when risk was actually resolved",
    )
    last_review_date = fields.Date(
        string="Last Review Date",
        help="Date of last risk review",
    )
    next_review_date = fields.Date(
        string="Next Review Date",
        help="Scheduled date for next review",
    )
    # Display and organization
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
        help="Additional notes and observations",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Generate unique reference on create."""
        for vals in vals_list:
            if vals.get("reference", "New") == "New":
                vals["reference"] = (
                    self.env["ir.sequence"].next_by_code("security.risk") or "New"
                )
        return super().create(vals_list)

    @api.depends("severity", "likelihood", "control_effectiveness")
    def _compute_risk_scores(self):
        """
        Calculate inherent and residual risk scores.

        Inherent score: severity (1-5) x likelihood (1-5) = 1-25
        Residual score: inherent x (1 - control_effectiveness/100)
        Risk level: based on residual score thresholds
        """
        severity_map = {
            "1_negligible": 1,
            "2_minor": 2,
            "3_moderate": 3,
            "4_major": 4,
            "5_critical": 5,
        }
        likelihood_map = {
            "1_rare": 1,
            "2_unlikely": 2,
            "3_possible": 3,
            "4_likely": 4,
            "5_almost_certain": 5,
        }
        for risk in self:
            sev = severity_map.get(risk.severity, 3)
            lik = likelihood_map.get(risk.likelihood, 3)
            risk.inherent_risk_score = sev * lik

            # Calculate residual score with control effectiveness
            effectiveness = risk.control_effectiveness or 0
            risk.residual_risk_score = int(
                risk.inherent_risk_score * (1 - effectiveness / 100)
            )

            # Determine risk level from residual score
            if risk.residual_risk_score >= 20:
                risk.risk_level = "critical"
            elif risk.residual_risk_score >= 12:
                risk.risk_level = "high"
            elif risk.residual_risk_score >= 6:
                risk.risk_level = "medium"
            else:
                risk.risk_level = "low"

    @api.depends("asset_ids")
    def _compute_asset_count(self):
        """Count affected assets."""
        for risk in self:
            risk.asset_count = len(risk.asset_ids)

    @api.depends("control_ids")
    def _compute_control_count(self):
        """Count mitigating controls."""
        for risk in self:
            risk.control_count = len(risk.control_ids)

    @api.depends("control_ids", "control_ids.status")
    def _compute_control_effectiveness(self):
        """
        Calculate control effectiveness percentage.

        Based on the implementation status of linked controls.
        """
        for risk in self:
            if not risk.control_ids:
                risk.control_effectiveness = 0.0
            else:
                implemented = risk.control_ids.filtered(
                    lambda c: c.status in ("implemented", "tested")
                )
                risk.control_effectiveness = (
                    len(implemented) / len(risk.control_ids)
                ) * 100

    @api.depends("risk_level")
    def _compute_color(self):
        """Set color based on risk level."""
        color_map = {
            "low": 10,  # Green
            "medium": 3,  # Yellow
            "high": 2,  # Orange
            "critical": 1,  # Red
        }
        for risk in self:
            risk.color = color_map.get(risk.risk_level, 0)

    @api.constrains("target_resolution_date", "identified_date")
    def _check_resolution_date(self):
        """Ensure target resolution is after identification."""
        for risk in self:
            if (
                risk.target_resolution_date
                and risk.identified_date
                and risk.target_resolution_date < risk.identified_date
            ):
                raise ValidationError(
                    "Target resolution date cannot be before identified date."
                )

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

    def action_view_controls(self):
        """Open related controls view."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Controls: {self.name}",
            "res_model": "security.control",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.control_ids.ids)],
        }

    def action_close_risk(self):
        """Mark risk as closed."""
        self.ensure_one()
        self.write({
            "status": "closed",
            "actual_resolution_date": fields.Date.today(),
        })

    def action_accept_risk(self):
        """Mark risk as accepted."""
        self.ensure_one()
        self.status = "accepted"
