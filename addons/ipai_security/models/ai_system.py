# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
AI System Model
===============

AI Systems Register for AI governance aligned with:
- NIST AI Risk Management Framework (AI RMF)
- ISO 42001 AI Management System (AIMS)

Tracks AI systems including:
- Claude Agent Service
- OCR Service (PaddleOCR-VL + OpenAI)
- MCP Coordinator
- Finance-SSC Expert
- Other AI-powered agents
"""
from odoo import api, fields, models


class AISystem(models.Model):
    """
    AI system registry record.

    Each record represents an AI-powered system or agent that requires
    governance oversight under NIST AI RMF and ISO 42001.

    Attributes:
        _name: Model technical name
        _description: Human-readable model description
        _inherit: Parent models for audit trail
        _order: Default ordering
    """

    _name = "ai.system"
    _description = "AI System"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(
        string="System Name",
        required=True,
        tracking=True,
        help="Name of the AI system (e.g., Agent Service, OCR Service)",
    )
    code = fields.Char(
        string="System Code",
        help="Unique identifier code for the AI system",
    )
    description = fields.Text(
        string="Description",
        help="Detailed description of the AI system and its purpose",
    )
    # System classification
    system_type = fields.Selection(
        [
            ("agent", "AI Agent"),
            ("model", "ML Model"),
            ("pipeline", "AI Pipeline"),
            ("assistant", "AI Assistant"),
            ("automation", "AI Automation"),
            ("analytics", "AI Analytics"),
            ("other", "Other"),
        ],
        string="System Type",
        default="agent",
        required=True,
        tracking=True,
        help="Type of AI system",
    )
    ai_category = fields.Selection(
        [
            ("generative", "Generative AI"),
            ("predictive", "Predictive AI"),
            ("classification", "Classification"),
            ("nlp", "Natural Language Processing"),
            ("cv", "Computer Vision"),
            ("recommendation", "Recommendation System"),
            ("automation", "Process Automation"),
            ("multi_modal", "Multi-Modal"),
        ],
        string="AI Category",
        help="Primary AI capability category",
    )
    # Model and provider details
    provider = fields.Selection(
        [
            ("anthropic", "Anthropic"),
            ("openai", "OpenAI"),
            ("google", "Google"),
            ("huggingface", "Hugging Face"),
            ("local", "Local/Self-Hosted"),
            ("custom", "Custom/In-House"),
            ("multiple", "Multiple Providers"),
            ("other", "Other"),
        ],
        string="AI Provider",
        tracking=True,
        help="Primary AI model/service provider",
    )
    models_used = fields.Char(
        string="Models Used",
        help="Specific model identifiers (e.g., claude-3.5-sonnet, gpt-4o)",
    )
    model_version = fields.Char(
        string="Model Version",
        help="Version of the model in use",
    )
    # Asset linkage
    primary_asset_id = fields.Many2one(
        "security.asset",
        string="Primary Asset",
        tracking=True,
        help="Primary infrastructure asset for this AI system",
    )
    asset_ids = fields.Many2many(
        "security.asset",
        "ai_system_asset_rel",
        "ai_system_id",
        "asset_id",
        string="Related Assets",
        help="All assets involved in this AI system",
    )
    # Data handling
    data_category_ids = fields.Many2many(
        "security.data.category",
        "ai_system_data_category_rel",
        "ai_system_id",
        "category_id",
        string="Data Categories",
        help="Types of data processed by this AI system",
    )
    handles_pii = fields.Boolean(
        string="Handles PII",
        compute="_compute_handles_pii",
        store=True,
        help="Whether this system processes personal information",
    )
    input_data_types = fields.Char(
        string="Input Data Types",
        help="Types of input data (e.g., text, images, documents)",
    )
    output_data_types = fields.Char(
        string="Output Data Types",
        help="Types of output data (e.g., text, decisions, recommendations)",
    )
    # Intended use and scope
    intended_use = fields.Text(
        string="Intended Use",
        required=True,
        help="Primary intended purpose and use cases for this AI system",
    )
    prohibited_uses = fields.Text(
        string="Prohibited Uses",
        help="Uses that are explicitly not allowed",
    )
    deployment_context = fields.Selection(
        [
            ("internal", "Internal Only"),
            ("customer_facing", "Customer-Facing"),
            ("decision_support", "Decision Support"),
            ("automation", "Fully Automated"),
            ("hybrid", "Human-in-the-Loop"),
        ],
        string="Deployment Context",
        default="internal",
        help="How the AI system is deployed and used",
    )
    user_types = fields.Char(
        string="User Types",
        help="Types of users who interact with this system",
    )
    # NIST AI RMF - Risk Assessment
    risk_level = fields.Selection(
        [
            ("minimal", "Minimal"),
            ("low", "Low"),
            ("moderate", "Moderate"),
            ("high", "High"),
            ("unacceptable", "Unacceptable"),
        ],
        string="AI Risk Level",
        default="moderate",
        tracking=True,
        help="Overall AI risk level per NIST AI RMF",
    )
    impact_category = fields.Selection(
        [
            ("individual", "Individual Rights/Safety"),
            ("group", "Group/Community"),
            ("organizational", "Organizational"),
            ("societal", "Societal"),
        ],
        string="Impact Category",
        help="Primary impact category if risk materializes",
    )
    # NIST AI RMF - Risk Types
    has_bias_risk = fields.Boolean(
        string="Bias Risk",
        default=False,
        help="Risk of algorithmic bias or discrimination",
    )
    has_transparency_risk = fields.Boolean(
        string="Transparency Risk",
        default=False,
        help="Risk related to lack of explainability",
    )
    has_privacy_risk = fields.Boolean(
        string="Privacy Risk",
        default=False,
        help="Risk of privacy violations",
    )
    has_security_risk = fields.Boolean(
        string="Security Risk",
        default=False,
        help="Risk of security vulnerabilities",
    )
    has_safety_risk = fields.Boolean(
        string="Safety Risk",
        default=False,
        help="Risk of harm to users or subjects",
    )
    has_accountability_risk = fields.Boolean(
        string="Accountability Risk",
        default=False,
        help="Risk of unclear accountability",
    )
    # Risk linkage
    risk_ids = fields.Many2many(
        "security.risk",
        "security_risk_ai_system_rel",
        "ai_system_id",
        "risk_id",
        string="Associated Risks",
        help="Security risks associated with this AI system",
    )
    risk_count = fields.Integer(
        string="Risk Count",
        compute="_compute_risk_count",
        store=True,
    )
    # Mitigations
    mitigation_measures = fields.Text(
        string="Mitigation Measures",
        help="Measures implemented to mitigate AI risks",
    )
    has_human_oversight = fields.Boolean(
        string="Human Oversight",
        default=True,
        help="Whether human oversight is in place",
    )
    oversight_description = fields.Text(
        string="Oversight Description",
        help="Description of human oversight mechanisms",
    )
    has_kill_switch = fields.Boolean(
        string="Kill Switch",
        default=False,
        help="Whether system can be immediately disabled",
    )
    # Evaluation and monitoring
    eval_status = fields.Selection(
        [
            ("not_evaluated", "Not Evaluated"),
            ("in_progress", "Evaluation In Progress"),
            ("partial", "Partially Evaluated"),
            ("completed", "Fully Evaluated"),
            ("needs_reevaluation", "Needs Re-evaluation"),
        ],
        string="Evaluation Status",
        default="not_evaluated",
        tracking=True,
        help="Status of AI system evaluation",
    )
    last_eval_date = fields.Date(
        string="Last Evaluation Date",
        tracking=True,
        help="Date of last formal evaluation",
    )
    next_eval_date = fields.Date(
        string="Next Evaluation Date",
        help="Scheduled date for next evaluation",
    )
    eval_frequency = fields.Selection(
        [
            ("per_deploy", "Per Deployment"),
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("annually", "Annually"),
        ],
        string="Evaluation Frequency",
        default="quarterly",
        help="How often the system should be evaluated",
    )
    performance_metrics = fields.Text(
        string="Performance Metrics",
        help="Key performance indicators for the AI system",
    )
    monitoring_approach = fields.Text(
        string="Monitoring Approach",
        help="How the system is monitored in production",
    )
    # Documentation
    documentation_url = fields.Char(
        string="Documentation URL",
        help="Link to technical documentation",
    )
    model_card_url = fields.Char(
        string="Model Card URL",
        help="Link to model card or system card",
    )
    # Status and ownership
    status = fields.Selection(
        [
            ("development", "In Development"),
            ("testing", "Testing"),
            ("staging", "Staging"),
            ("production", "Production"),
            ("deprecated", "Deprecated"),
            ("retired", "Retired"),
        ],
        string="Status",
        default="development",
        required=True,
        tracking=True,
        help="Current lifecycle status",
    )
    owner_id = fields.Many2one(
        "res.users",
        string="System Owner",
        tracking=True,
        help="User responsible for this AI system",
    )
    ai_lead_id = fields.Many2one(
        "res.users",
        string="AI Lead",
        tracking=True,
        help="AI governance lead for this system",
    )
    responsible_team = fields.Char(
        string="Responsible Team",
        help="Team responsible for the AI system",
    )
    # Dates
    deployment_date = fields.Date(
        string="Deployment Date",
        help="Date when system was deployed to production",
    )
    created_date = fields.Date(
        string="Created Date",
        default=fields.Date.today,
        help="Date when system was registered",
    )
    # Display
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

    _sql_constraints = [
        (
            "code_unique",
            "UNIQUE(code)",
            "AI system code must be unique!",
        ),
    ]

    @api.depends("data_category_ids", "data_category_ids.dpa_classification")
    def _compute_handles_pii(self):
        """Determine if AI system handles personal information."""
        for system in self:
            system.handles_pii = any(
                cat.dpa_classification in ("personal", "sensitive_personal", "privileged")
                for cat in system.data_category_ids
            )

    @api.depends("risk_ids")
    def _compute_risk_count(self):
        """Count associated risks."""
        for system in self:
            system.risk_count = len(system.risk_ids)

    @api.depends("risk_level", "eval_status")
    def _compute_color(self):
        """Set color based on risk level and evaluation status."""
        for system in self:
            if system.risk_level in ("high", "unacceptable"):
                system.color = 1  # Red
            elif system.risk_level == "moderate" or system.eval_status == "not_evaluated":
                system.color = 3  # Yellow
            else:
                system.color = 10  # Green

    def action_start_evaluation(self):
        """Mark evaluation as in progress."""
        self.ensure_one()
        self.eval_status = "in_progress"

    def action_complete_evaluation(self):
        """Mark evaluation as completed."""
        self.ensure_one()
        self.write({
            "eval_status": "completed",
            "last_eval_date": fields.Date.today(),
        })

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
