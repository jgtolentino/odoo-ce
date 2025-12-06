# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Security Audit Model
====================

Audit and assessment management for the Security & Compliance Workbench.
Tracks:
- Internal and external audits
- Assessment scopes and frameworks
- Findings and recommendations
- Evidence and documentation
"""
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SecurityAudit(models.Model):
    """
    Security audit record.

    Each record represents a security audit or assessment conducted
    against one or more compliance frameworks.

    Attributes:
        _name: Model technical name
        _description: Human-readable model description
        _inherit: Parent models for audit trail
        _order: Default ordering
    """

    _name = "security.audit"
    _description = "Security Audit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_date DESC, id DESC"

    name = fields.Char(
        string="Audit Name",
        required=True,
        tracking=True,
        help="Name of the audit or assessment",
    )
    reference = fields.Char(
        string="Reference",
        readonly=True,
        copy=False,
        default="New",
        help="Unique audit reference number",
    )
    description = fields.Text(
        string="Description",
        help="Detailed description and objectives of the audit",
    )
    # Audit type and scope
    audit_type = fields.Selection(
        [
            ("internal", "Internal Audit"),
            ("external", "External Audit"),
            ("self_assessment", "Self-Assessment"),
            ("readiness", "Readiness Assessment"),
            ("certification", "Certification Audit"),
            ("surveillance", "Surveillance Audit"),
        ],
        string="Audit Type",
        default="internal",
        required=True,
        tracking=True,
        help="Type of audit",
    )
    framework_ids = fields.Many2many(
        "security.framework",
        "security_audit_framework_rel",
        "audit_id",
        "framework_id",
        string="Frameworks",
        required=True,
        help="Compliance frameworks covered by this audit",
    )
    asset_ids = fields.Many2many(
        "security.asset",
        "security_audit_asset_rel",
        "audit_id",
        "asset_id",
        string="Assets in Scope",
        help="Assets included in the audit scope",
    )
    asset_count = fields.Integer(
        string="Asset Count",
        compute="_compute_asset_count",
        store=True,
    )
    control_ids = fields.Many2many(
        "security.control",
        "security_audit_control_rel",
        "audit_id",
        "control_id",
        string="Controls Assessed",
        help="Controls evaluated in this audit",
    )
    control_count = fields.Integer(
        string="Control Count",
        compute="_compute_control_count",
        store=True,
    )
    scope_description = fields.Text(
        string="Scope Description",
        help="Detailed description of audit scope",
    )
    # Timeline
    start_date = fields.Date(
        string="Start Date",
        required=True,
        tracking=True,
        help="Planned or actual start date",
    )
    end_date = fields.Date(
        string="End Date",
        tracking=True,
        help="Planned or actual end date",
    )
    report_date = fields.Date(
        string="Report Date",
        tracking=True,
        help="Date the audit report was issued",
    )
    # Status
    status = fields.Selection(
        [
            ("planned", "Planned"),
            ("in_progress", "In Progress"),
            ("fieldwork_complete", "Fieldwork Complete"),
            ("report_draft", "Report Draft"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="planned",
        required=True,
        tracking=True,
        help="Current audit status",
    )
    # Results
    overall_rating = fields.Selection(
        [
            ("satisfactory", "Satisfactory"),
            ("needs_improvement", "Needs Improvement"),
            ("unsatisfactory", "Unsatisfactory"),
            ("not_rated", "Not Rated"),
        ],
        string="Overall Rating",
        default="not_rated",
        tracking=True,
        help="Overall audit rating",
    )
    controls_tested = fields.Integer(
        string="Controls Tested",
        help="Number of controls tested",
    )
    controls_passed = fields.Integer(
        string="Controls Passed",
        help="Number of controls that passed testing",
    )
    controls_failed = fields.Integer(
        string="Controls Failed",
        help="Number of controls that failed testing",
    )
    pass_rate = fields.Float(
        string="Pass Rate %",
        compute="_compute_pass_rate",
        store=True,
        help="Percentage of controls that passed",
    )
    # Findings
    finding_ids = fields.One2many(
        "security.audit.finding",
        "audit_id",
        string="Findings",
        help="Audit findings and observations",
    )
    finding_count = fields.Integer(
        string="Finding Count",
        compute="_compute_finding_count",
        store=True,
    )
    critical_findings = fields.Integer(
        string="Critical Findings",
        compute="_compute_finding_count",
        store=True,
    )
    # Documentation
    report_url = fields.Char(
        string="Report URL",
        help="Link to the audit report",
    )
    evidence_url = fields.Char(
        string="Evidence URL",
        help="Link to audit evidence repository",
    )
    # Auditor information
    auditor_type = fields.Selection(
        [
            ("internal", "Internal Team"),
            ("external_firm", "External Firm"),
            ("regulator", "Regulator"),
        ],
        string="Auditor Type",
        help="Type of auditor",
    )
    auditor_name = fields.Char(
        string="Auditor/Firm Name",
        help="Name of auditor or audit firm",
    )
    lead_auditor = fields.Char(
        string="Lead Auditor",
        help="Name of lead auditor",
    )
    # Ownership
    owner_id = fields.Many2one(
        "res.users",
        string="Audit Owner",
        tracking=True,
        help="User responsible for coordinating the audit",
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

    @api.model_create_multi
    def create(self, vals_list):
        """Generate unique reference on create."""
        for vals in vals_list:
            if vals.get("reference", "New") == "New":
                vals["reference"] = (
                    self.env["ir.sequence"].next_by_code("security.audit") or "New"
                )
        return super().create(vals_list)

    @api.depends("asset_ids")
    def _compute_asset_count(self):
        """Count assets in scope."""
        for audit in self:
            audit.asset_count = len(audit.asset_ids)

    @api.depends("control_ids")
    def _compute_control_count(self):
        """Count controls assessed."""
        for audit in self:
            audit.control_count = len(audit.control_ids)

    @api.depends("finding_ids", "finding_ids.severity")
    def _compute_finding_count(self):
        """Count findings by severity."""
        for audit in self:
            audit.finding_count = len(audit.finding_ids)
            audit.critical_findings = len(
                audit.finding_ids.filtered(lambda f: f.severity == "critical")
            )

    @api.depends("controls_tested", "controls_passed")
    def _compute_pass_rate(self):
        """Calculate control pass rate."""
        for audit in self:
            if audit.controls_tested:
                audit.pass_rate = (audit.controls_passed / audit.controls_tested) * 100
            else:
                audit.pass_rate = 0.0

    @api.depends("status", "overall_rating")
    def _compute_color(self):
        """Set color based on status and rating."""
        for audit in self:
            if audit.status == "cancelled":
                audit.color = 0  # Gray
            elif audit.overall_rating == "unsatisfactory":
                audit.color = 1  # Red
            elif audit.overall_rating == "needs_improvement":
                audit.color = 3  # Yellow
            elif audit.overall_rating == "satisfactory":
                audit.color = 10  # Green
            else:
                audit.color = 4  # Blue

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        """Ensure end date is after start date."""
        for audit in self:
            if audit.end_date and audit.start_date and audit.end_date < audit.start_date:
                raise ValidationError("End date cannot be before start date.")

    def action_start_audit(self):
        """Start the audit."""
        self.ensure_one()
        self.status = "in_progress"

    def action_complete_fieldwork(self):
        """Mark fieldwork as complete."""
        self.ensure_one()
        self.status = "fieldwork_complete"

    def action_draft_report(self):
        """Mark report as draft."""
        self.ensure_one()
        self.status = "report_draft"

    def action_complete_audit(self):
        """Complete the audit."""
        self.ensure_one()
        self.write({
            "status": "completed",
            "report_date": fields.Date.today(),
        })


class SecurityAuditFinding(models.Model):
    """
    Audit finding record.

    Each finding represents an observation or issue identified during
    an audit.
    """

    _name = "security.audit.finding"
    _description = "Audit Finding"
    _inherit = ["mail.thread"]
    _order = "severity DESC, id DESC"

    name = fields.Char(
        string="Finding Title",
        required=True,
        tracking=True,
        help="Brief title of the finding",
    )
    reference = fields.Char(
        string="Reference",
        readonly=True,
        copy=False,
        default="New",
    )
    audit_id = fields.Many2one(
        "security.audit",
        string="Audit",
        required=True,
        ondelete="cascade",
        help="Parent audit",
    )
    description = fields.Text(
        string="Description",
        required=True,
        help="Detailed description of the finding",
    )
    severity = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        string="Severity",
        default="medium",
        required=True,
        tracking=True,
        help="Severity of the finding",
    )
    finding_type = fields.Selection(
        [
            ("observation", "Observation"),
            ("nonconformity", "Non-Conformity"),
            ("opportunity", "Opportunity for Improvement"),
            ("exception", "Control Exception"),
        ],
        string="Finding Type",
        default="observation",
        required=True,
        help="Type of audit finding",
    )
    control_id = fields.Many2one(
        "security.control",
        string="Related Control",
        help="Control this finding relates to",
    )
    asset_ids = fields.Many2many(
        "security.asset",
        "security_audit_finding_asset_rel",
        "finding_id",
        "asset_id",
        string="Affected Assets",
        help="Assets affected by this finding",
    )
    root_cause = fields.Text(
        string="Root Cause",
        help="Identified root cause",
    )
    recommendation = fields.Text(
        string="Recommendation",
        help="Auditor's recommendation",
    )
    management_response = fields.Text(
        string="Management Response",
        help="Management's response to the finding",
    )
    remediation_plan = fields.Text(
        string="Remediation Plan",
        help="Plan to address the finding",
    )
    target_date = fields.Date(
        string="Target Remediation Date",
        help="Target date for remediation",
    )
    actual_date = fields.Date(
        string="Actual Remediation Date",
        help="Actual date remediation was completed",
    )
    status = fields.Selection(
        [
            ("open", "Open"),
            ("in_progress", "In Progress"),
            ("remediated", "Remediated"),
            ("verified", "Verified"),
            ("closed", "Closed"),
            ("accepted", "Risk Accepted"),
        ],
        string="Status",
        default="open",
        required=True,
        tracking=True,
        help="Current status of the finding",
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Assigned To",
        tracking=True,
        help="User responsible for remediation",
    )
    evidence_url = fields.Char(
        string="Evidence URL",
        help="Link to remediation evidence",
    )
    color = fields.Integer(
        string="Color Index",
        compute="_compute_color",
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Generate unique reference on create."""
        for vals in vals_list:
            if vals.get("reference", "New") == "New":
                vals["reference"] = (
                    self.env["ir.sequence"].next_by_code("security.audit.finding")
                    or "New"
                )
        return super().create(vals_list)

    @api.depends("severity", "status")
    def _compute_color(self):
        """Set color based on severity and status."""
        for finding in self:
            if finding.status in ("closed", "verified"):
                finding.color = 10  # Green
            elif finding.severity == "critical":
                finding.color = 1  # Red
            elif finding.severity == "high":
                finding.color = 2  # Orange
            else:
                finding.color = 3  # Yellow
