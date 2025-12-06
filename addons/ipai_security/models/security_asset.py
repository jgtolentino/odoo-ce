# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Security Asset Model
====================

Central asset inventory for the Security & Compliance Workbench.
Tracks all production assets including:
- Applications and services
- AI agents and systems
- Droplets and infrastructure
- Databases and data stores
- Storage buckets
"""
from odoo import api, fields, models


class SecurityAsset(models.Model):
    """
    Security asset inventory record.

    Each asset represents a trackable component of the fin-workspace
    infrastructure that needs security governance.

    Attributes:
        _name: Model technical name
        _description: Human-readable model description
        _inherit: Parent models for audit trail
        _order: Default ordering for lists
    """

    _name = "security.asset"
    _description = "Security Asset"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(
        string="Asset Name",
        required=True,
        tracking=True,
        help="Name of the asset (e.g., Agent Service, OCR Droplet)",
    )
    code = fields.Char(
        string="Asset Code",
        help="Unique identifier code for the asset",
    )
    asset_type = fields.Selection(
        [
            ("application", "Application/Service"),
            ("agent", "AI Agent"),
            ("droplet", "Droplet/VM"),
            ("database", "Database"),
            ("bucket", "Storage Bucket"),
            ("api", "API/Endpoint"),
            ("network", "Network Component"),
            ("other", "Other"),
        ],
        string="Asset Type",
        required=True,
        default="application",
        tracking=True,
        help="Type of infrastructure asset",
    )
    environment = fields.Selection(
        [
            ("production", "Production"),
            ("staging", "Staging"),
            ("development", "Development"),
            ("testing", "Testing"),
        ],
        string="Environment",
        default="production",
        required=True,
        tracking=True,
        help="Deployment environment",
    )
    description = fields.Text(
        string="Description",
        help="Detailed description of the asset and its purpose",
    )
    url = fields.Char(
        string="URL/Endpoint",
        help="Primary URL or endpoint for the asset",
    )
    # External IDs for integration
    do_droplet_id = fields.Char(
        string="DigitalOcean ID",
        help="DigitalOcean droplet or resource ID",
    )
    supabase_id = fields.Char(
        string="Supabase ID",
        help="Supabase project or resource ID",
    )
    # Ownership and responsibility
    owner_user_id = fields.Many2one(
        "res.users",
        string="Owner",
        tracking=True,
        help="User responsible for this asset",
    )
    owner_role = fields.Selection(
        [
            ("owner", "Owner"),
            ("security_officer", "Security Officer"),
            ("engineer", "Engineer"),
            ("ai_lead", "AI Lead"),
        ],
        string="Owner Role",
        help="Role of the asset owner",
    )
    team = fields.Char(
        string="Responsible Team",
        help="Team responsible for the asset",
    )
    # Data classification
    data_category_ids = fields.Many2many(
        "security.data.category",
        "security_asset_data_category_rel",
        "asset_id",
        "category_id",
        string="Data Categories",
        help="Types of data processed by this asset",
    )
    handles_pii = fields.Boolean(
        string="Handles PII",
        compute="_compute_handles_pii",
        store=True,
        help="Whether this asset processes personal information",
    )
    handles_sensitive = fields.Boolean(
        string="Handles Sensitive Data",
        compute="_compute_handles_sensitive",
        store=True,
        help="Whether this asset processes sensitive personal information",
    )
    # Risk assessment
    risk_level = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Risk Level",
        default="medium",
        tracking=True,
        help="Current risk level assessment",
    )
    risk_score = fields.Integer(
        string="Risk Score",
        compute="_compute_risk_score",
        store=True,
        help="Calculated risk score (0-100)",
    )
    # Status and audit
    status = fields.Selection(
        [
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("decommissioned", "Decommissioned"),
            ("pending_review", "Pending Review"),
        ],
        string="Status",
        default="active",
        tracking=True,
        help="Operational status of the asset",
    )
    in_scope = fields.Boolean(
        string="In Compliance Scope",
        default=True,
        tracking=True,
        help="Whether this asset is in scope for compliance frameworks",
    )
    last_audit_date = fields.Date(
        string="Last Audit Date",
        tracking=True,
        help="Date of last security audit",
    )
    next_audit_date = fields.Date(
        string="Next Audit Date",
        help="Scheduled date for next security audit",
    )
    # Related records
    risk_ids = fields.Many2many(
        "security.risk",
        "security_asset_risk_rel",
        "asset_id",
        "risk_id",
        string="Related Risks",
        help="Security risks associated with this asset",
    )
    risk_count = fields.Integer(
        string="Risk Count",
        compute="_compute_risk_count",
        store=True,
        help="Number of associated risks",
    )
    control_ids = fields.Many2many(
        "security.control",
        "security_asset_control_rel",
        "asset_id",
        "control_id",
        string="Applied Controls",
        help="Security controls applied to this asset",
    )
    control_count = fields.Integer(
        string="Control Count",
        compute="_compute_control_count",
        store=True,
        help="Number of applied controls",
    )
    ai_system_ids = fields.One2many(
        "ai.system",
        "primary_asset_id",
        string="AI Systems",
        help="AI systems associated with this asset",
    )
    incident_ids = fields.Many2many(
        "security.incident",
        "security_incident_asset_rel",
        "asset_id",
        "incident_id",
        string="Incidents",
        help="Security incidents involving this asset",
    )
    incident_count = fields.Integer(
        string="Incident Count",
        compute="_compute_incident_count",
        store=True,
        help="Number of security incidents",
    )
    # Technical details
    tech_stack = fields.Char(
        string="Technology Stack",
        help="Technologies used (e.g., Python, Node.js, PostgreSQL)",
    )
    version = fields.Char(
        string="Current Version",
        help="Current deployed version",
    )
    dependencies = fields.Text(
        string="Dependencies",
        help="Key dependencies and integrations",
    )
    # Display
    color = fields.Integer(
        string="Color Index",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    notes = fields.Html(
        string="Notes",
        help="Additional notes and documentation",
    )

    _sql_constraints = [
        (
            "code_unique",
            "UNIQUE(code)",
            "Asset code must be unique!",
        ),
    ]

    @api.depends("data_category_ids", "data_category_ids.dpa_classification")
    def _compute_handles_pii(self):
        """Determine if asset handles personal information."""
        for asset in self:
            asset.handles_pii = any(
                cat.dpa_classification in ("personal", "sensitive_personal", "privileged")
                for cat in asset.data_category_ids
            )

    @api.depends("data_category_ids", "data_category_ids.dpa_classification")
    def _compute_handles_sensitive(self):
        """Determine if asset handles sensitive personal information."""
        for asset in self:
            asset.handles_sensitive = any(
                cat.dpa_classification in ("sensitive_personal", "privileged")
                for cat in asset.data_category_ids
            )

    @api.depends("risk_ids")
    def _compute_risk_count(self):
        """Count associated risks."""
        for asset in self:
            asset.risk_count = len(asset.risk_ids)

    @api.depends("control_ids")
    def _compute_control_count(self):
        """Count applied controls."""
        for asset in self:
            asset.control_count = len(asset.control_ids)

    @api.depends("incident_ids")
    def _compute_incident_count(self):
        """Count security incidents."""
        for asset in self:
            asset.incident_count = len(asset.incident_ids)

    @api.depends("risk_level", "handles_sensitive", "risk_count")
    def _compute_risk_score(self):
        """
        Calculate composite risk score.

        Score is based on:
        - Base score from risk_level
        - Bonus for handling sensitive data
        - Additional points for open risks
        """
        level_scores = {
            "low": 20,
            "medium": 40,
            "high": 70,
            "critical": 90,
        }
        for asset in self:
            score = level_scores.get(asset.risk_level, 40)
            if asset.handles_sensitive:
                score += 10
            # Add points for each open risk (capped)
            open_risks = asset.risk_ids.filtered(
                lambda r: r.status in ("open", "in_progress")
            )
            score += min(len(open_risks) * 5, 20)
            asset.risk_score = min(score, 100)

    def action_view_risks(self):
        """Open related risks view."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Risks: {self.name}",
            "res_model": "security.risk",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.risk_ids.ids)],
            "context": {"default_asset_ids": [(6, 0, [self.id])]},
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
            "context": {"default_asset_ids": [(6, 0, [self.id])]},
        }

    def action_view_incidents(self):
        """Open related incidents view."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": f"Incidents: {self.name}",
            "res_model": "security.incident",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.incident_ids.ids)],
            "context": {"default_asset_ids": [(6, 0, [self.id])]},
        }

    def action_schedule_audit(self):
        """Open wizard to schedule security audit."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Schedule Audit",
            "res_model": "security.audit",
            "view_mode": "form",
            "target": "new",
            "context": {"default_asset_ids": [(6, 0, [self.id])]},
        }
