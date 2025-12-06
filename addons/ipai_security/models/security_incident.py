# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Security Incident Model
=======================

Security incident tracking for the Security & Compliance Workbench.
Tracks:
- Security breaches and events
- Incident response and resolution
- Lessons learned
- Root cause analysis
"""
from odoo import api, fields, models


class SecurityIncident(models.Model):
    """
    Security incident record.

    Each record represents a security event or breach that requires
    tracking, response, and potential reporting.

    Attributes:
        _name: Model technical name
        _description: Human-readable model description
        _inherit: Parent models for audit trail
        _order: Default ordering (most recent first)
    """

    _name = "security.incident"
    _description = "Security Incident"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "detected_date DESC, id DESC"

    name = fields.Char(
        string="Incident Title",
        required=True,
        tracking=True,
        help="Brief title describing the incident",
    )
    reference = fields.Char(
        string="Reference",
        readonly=True,
        copy=False,
        default="New",
        help="Unique incident reference number",
    )
    description = fields.Text(
        string="Description",
        required=True,
        help="Detailed description of the incident",
    )
    # Classification
    incident_type = fields.Selection(
        [
            ("breach", "Data Breach"),
            ("unauthorized_access", "Unauthorized Access"),
            ("malware", "Malware/Virus"),
            ("phishing", "Phishing/Social Engineering"),
            ("dos", "Denial of Service"),
            ("data_loss", "Data Loss"),
            ("misconfiguration", "Misconfiguration"),
            ("vulnerability", "Vulnerability Exploitation"),
            ("insider", "Insider Threat"),
            ("ai_failure", "AI System Failure"),
            ("other", "Other"),
        ],
        string="Incident Type",
        default="other",
        required=True,
        tracking=True,
        help="Type of security incident",
    )
    severity = fields.Selection(
        [
            ("1_low", "Low"),
            ("2_medium", "Medium"),
            ("3_high", "High"),
            ("4_critical", "Critical"),
        ],
        string="Severity",
        default="2_medium",
        required=True,
        tracking=True,
        help="Severity level of the incident",
    )
    priority = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("urgent", "Urgent"),
        ],
        string="Priority",
        default="medium",
        required=True,
        tracking=True,
        help="Response priority",
    )
    # Status and workflow
    status = fields.Selection(
        [
            ("detected", "Detected"),
            ("investigating", "Investigating"),
            ("contained", "Contained"),
            ("eradicated", "Eradicated"),
            ("recovering", "Recovering"),
            ("closed", "Closed"),
        ],
        string="Status",
        default="detected",
        required=True,
        tracking=True,
        help="Current status in incident response workflow",
    )
    # Affected assets
    asset_ids = fields.Many2many(
        "security.incident",
        "security_incident_asset_rel",
        "incident_id",
        "asset_id",
        string="Affected Assets",
        help="Assets affected by this incident",
    )
    asset_count = fields.Integer(
        string="Asset Count",
        compute="_compute_asset_count",
        store=True,
    )
    # AI system involvement
    ai_system_ids = fields.Many2many(
        "ai.system",
        "security_incident_ai_system_rel",
        "incident_id",
        "ai_system_id",
        string="Involved AI Systems",
        help="AI systems involved in the incident",
    )
    is_ai_related = fields.Boolean(
        string="AI-Related Incident",
        default=False,
        help="Whether incident involves AI systems",
    )
    # Data impact
    data_categories_impacted = fields.Many2many(
        "security.data.category",
        "security_incident_data_category_rel",
        "incident_id",
        "category_id",
        string="Data Categories Impacted",
        help="Types of data affected",
    )
    pii_involved = fields.Boolean(
        string="PII Involved",
        default=False,
        help="Whether personal information was involved",
    )
    records_affected = fields.Integer(
        string="Records Affected",
        help="Number of records potentially affected",
    )
    # Timeline
    detected_date = fields.Datetime(
        string="Detected Date",
        default=fields.Datetime.now,
        required=True,
        tracking=True,
        help="When the incident was detected",
    )
    reported_date = fields.Datetime(
        string="Reported Date",
        tracking=True,
        help="When the incident was reported",
    )
    contained_date = fields.Datetime(
        string="Contained Date",
        tracking=True,
        help="When the incident was contained",
    )
    resolved_date = fields.Datetime(
        string="Resolved Date",
        tracking=True,
        help="When the incident was resolved",
    )
    # Response
    response_actions = fields.Text(
        string="Response Actions",
        help="Actions taken to respond to the incident",
    )
    containment_actions = fields.Text(
        string="Containment Actions",
        help="Actions taken to contain the incident",
    )
    eradication_actions = fields.Text(
        string="Eradication Actions",
        help="Actions taken to eradicate the threat",
    )
    recovery_actions = fields.Text(
        string="Recovery Actions",
        help="Actions taken for recovery",
    )
    # Root cause and lessons learned
    root_cause = fields.Text(
        string="Root Cause",
        help="Identified root cause of the incident",
    )
    lessons_learned = fields.Text(
        string="Lessons Learned",
        help="Key takeaways from the incident",
    )
    preventive_measures = fields.Text(
        string="Preventive Measures",
        help="Measures to prevent recurrence",
    )
    # Notifications and reporting
    requires_notification = fields.Boolean(
        string="Requires Notification",
        default=False,
        help="Whether incident requires external notification",
    )
    notification_deadline = fields.Datetime(
        string="Notification Deadline",
        help="Deadline for required notifications (e.g., 72 hours for GDPR)",
    )
    npc_notified = fields.Boolean(
        string="NPC Notified",
        default=False,
        help="Whether National Privacy Commission was notified (PH DPA)",
    )
    npc_notification_date = fields.Datetime(
        string="NPC Notification Date",
        help="Date NPC was notified",
    )
    affected_parties_notified = fields.Boolean(
        string="Affected Parties Notified",
        default=False,
        help="Whether affected data subjects were notified",
    )
    # Related risks and controls
    related_risk_ids = fields.Many2many(
        "security.risk",
        "security_incident_risk_rel",
        "incident_id",
        "risk_id",
        string="Related Risks",
        help="Risks that may have contributed to this incident",
    )
    failed_control_ids = fields.Many2many(
        "security.control",
        "security_incident_control_rel",
        "incident_id",
        "control_id",
        string="Failed Controls",
        help="Controls that failed or were bypassed",
    )
    # Ownership
    reporter_id = fields.Many2one(
        "res.users",
        string="Reported By",
        tracking=True,
        help="User who reported the incident",
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Incident Owner",
        tracking=True,
        help="User responsible for managing the incident",
    )
    responder_ids = fields.Many2many(
        "res.users",
        "security_incident_responder_rel",
        "incident_id",
        "user_id",
        string="Response Team",
        help="Users involved in incident response",
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
        help="Additional notes and documentation",
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Generate unique reference on create."""
        for vals in vals_list:
            if vals.get("reference", "New") == "New":
                vals["reference"] = (
                    self.env["ir.sequence"].next_by_code("security.incident") or "New"
                )
        return super().create(vals_list)

    @api.depends("asset_ids")
    def _compute_asset_count(self):
        """Count affected assets."""
        for incident in self:
            incident.asset_count = len(incident.asset_ids)

    @api.depends("severity", "status")
    def _compute_color(self):
        """Set color based on severity and status."""
        for incident in self:
            if incident.status == "closed":
                incident.color = 10  # Green
            elif incident.severity == "4_critical":
                incident.color = 1  # Red
            elif incident.severity == "3_high":
                incident.color = 2  # Orange
            elif incident.severity == "2_medium":
                incident.color = 3  # Yellow
            else:
                incident.color = 10  # Green

    def action_investigate(self):
        """Move to investigating status."""
        self.ensure_one()
        self.status = "investigating"

    def action_contain(self):
        """Move to contained status."""
        self.ensure_one()
        self.write({
            "status": "contained",
            "contained_date": fields.Datetime.now(),
        })

    def action_eradicate(self):
        """Move to eradicated status."""
        self.ensure_one()
        self.status = "eradicated"

    def action_recover(self):
        """Move to recovering status."""
        self.ensure_one()
        self.status = "recovering"

    def action_close(self):
        """Close the incident."""
        self.ensure_one()
        self.write({
            "status": "closed",
            "resolved_date": fields.Datetime.now(),
        })
