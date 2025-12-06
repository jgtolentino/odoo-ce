# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Security Data Flow Model
========================

Data flow mapping for PH DPA compliance tracking.
Maps data flows between assets including:
- Source and destination assets
- Data categories transferred
- Lawful basis for processing
- Purpose and retention policies
"""
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class SecurityDataFlow(models.Model):
    """
    Data flow record for compliance mapping.

    Each record represents a data flow between two assets, documenting
    what data is transferred, why, and under what legal basis.

    Attributes:
        _name: Model technical name
        _description: Human-readable model description
        _inherit: Parent models for audit trail
        _order: Default ordering
    """

    _name = "security.data.flow"
    _description = "Security Data Flow"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "source_asset_id, target_asset_id"

    name = fields.Char(
        string="Flow Name",
        compute="_compute_name",
        store=True,
        help="Generated name for the data flow",
    )
    reference = fields.Char(
        string="Reference",
        readonly=True,
        copy=False,
        default="New",
        help="Unique reference number",
    )
    description = fields.Text(
        string="Description",
        help="Detailed description of the data flow",
    )
    # Source and destination
    source_asset_id = fields.Many2one(
        "security.asset",
        string="Source Asset",
        required=True,
        tracking=True,
        help="Asset where data originates",
    )
    target_asset_id = fields.Many2one(
        "security.asset",
        string="Target Asset",
        required=True,
        tracking=True,
        help="Asset where data is sent",
    )
    # Data classification
    data_category_ids = fields.Many2many(
        "security.data.category",
        "security_data_flow_category_rel",
        "flow_id",
        "category_id",
        string="Data Categories",
        required=True,
        help="Types of data transferred in this flow",
    )
    contains_pii = fields.Boolean(
        string="Contains PII",
        compute="_compute_contains_pii",
        store=True,
        help="Whether flow contains personal information",
    )
    contains_sensitive = fields.Boolean(
        string="Contains Sensitive Data",
        compute="_compute_contains_sensitive",
        store=True,
        help="Whether flow contains sensitive personal information",
    )
    # PH DPA compliance
    lawful_basis_id = fields.Many2one(
        "security.lawful.basis",
        string="Lawful Basis",
        tracking=True,
        help="Legal basis for processing under PH DPA",
    )
    purpose = fields.Text(
        string="Processing Purpose",
        required=True,
        help="Purpose for which data is processed",
    )
    is_purpose_documented = fields.Boolean(
        string="Purpose Documented",
        default=False,
        help="Whether the purpose is formally documented",
    )
    # Retention and handling
    retention_period = fields.Integer(
        string="Retention Period (Days)",
        help="How long data is retained (0 = indefinite)",
    )
    retention_policy = fields.Text(
        string="Retention Policy",
        help="Details of data retention and deletion policies",
    )
    # Data subjects
    data_subject_types = fields.Selection(
        [
            ("employees", "Employees"),
            ("customers", "Customers"),
            ("vendors", "Vendors"),
            ("partners", "Partners"),
            ("public", "Public"),
            ("mixed", "Mixed"),
        ],
        string="Data Subject Types",
        help="Types of individuals whose data is processed",
    )
    estimated_volume = fields.Char(
        string="Estimated Volume",
        help="Estimated number of records processed",
    )
    # Transfer details
    transfer_method = fields.Selection(
        [
            ("api", "API"),
            ("database", "Direct Database"),
            ("file", "File Transfer"),
            ("message_queue", "Message Queue"),
            ("manual", "Manual"),
            ("other", "Other"),
        ],
        string="Transfer Method",
        default="api",
        help="How data is transferred between assets",
    )
    is_encrypted = fields.Boolean(
        string="Encrypted in Transit",
        default=True,
        help="Whether data is encrypted during transfer",
    )
    encryption_method = fields.Char(
        string="Encryption Method",
        help="Encryption protocol used (e.g., TLS 1.3, AES-256)",
    )
    # Cross-border considerations
    is_cross_border = fields.Boolean(
        string="Cross-Border Transfer",
        default=False,
        help="Whether data crosses national borders",
    )
    destination_country = fields.Char(
        string="Destination Country",
        help="Country where data is transferred to",
    )
    transfer_mechanism = fields.Selection(
        [
            ("adequacy", "Adequacy Decision"),
            ("consent", "Data Subject Consent"),
            ("contract", "Contractual Clauses"),
            ("bcr", "Binding Corporate Rules"),
            ("exception", "Legal Exception"),
        ],
        string="Transfer Mechanism",
        help="Legal mechanism for cross-border transfer",
    )
    # Third parties
    involves_third_party = fields.Boolean(
        string="Involves Third Party",
        default=False,
        help="Whether a third party processor is involved",
    )
    third_party_name = fields.Char(
        string="Third Party Name",
        help="Name of third party processor",
    )
    dpa_contract_in_place = fields.Boolean(
        string="DPA Contract in Place",
        default=False,
        help="Whether data processing agreement is signed",
    )
    # Status and review
    status = fields.Selection(
        [
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("pending_review", "Pending Review"),
            ("non_compliant", "Non-Compliant"),
        ],
        string="Status",
        default="pending_review",
        required=True,
        tracking=True,
        help="Compliance status of this data flow",
    )
    compliance_gap = fields.Boolean(
        string="Has Compliance Gap",
        compute="_compute_compliance_gap",
        store=True,
        help="Whether this flow has identified compliance issues",
    )
    compliance_notes = fields.Text(
        string="Compliance Notes",
        help="Notes on compliance status and gaps",
    )
    last_review_date = fields.Date(
        string="Last Review Date",
        tracking=True,
        help="Date of last compliance review",
    )
    next_review_date = fields.Date(
        string="Next Review Date",
        help="Scheduled date for next review",
    )
    # Ownership
    owner_id = fields.Many2one(
        "res.users",
        string="Flow Owner",
        tracking=True,
        help="User responsible for this data flow",
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
                    self.env["ir.sequence"].next_by_code("security.data.flow") or "New"
                )
        return super().create(vals_list)

    @api.depends("source_asset_id", "target_asset_id")
    def _compute_name(self):
        """Generate name from source and target assets."""
        for flow in self:
            if flow.source_asset_id and flow.target_asset_id:
                flow.name = f"{flow.source_asset_id.name} → {flow.target_asset_id.name}"
            else:
                flow.name = "New Data Flow"

    @api.depends("data_category_ids", "data_category_ids.dpa_classification")
    def _compute_contains_pii(self):
        """Determine if flow contains personal information."""
        for flow in self:
            flow.contains_pii = any(
                cat.dpa_classification in ("personal", "sensitive_personal", "privileged")
                for cat in flow.data_category_ids
            )

    @api.depends("data_category_ids", "data_category_ids.dpa_classification")
    def _compute_contains_sensitive(self):
        """Determine if flow contains sensitive personal information."""
        for flow in self:
            flow.contains_sensitive = any(
                cat.dpa_classification in ("sensitive_personal", "privileged")
                for cat in flow.data_category_ids
            )

    @api.depends("contains_pii", "lawful_basis_id", "is_encrypted", "status")
    def _compute_compliance_gap(self):
        """
        Identify compliance gaps in data flows.

        Gaps exist when:
        - PII without lawful basis
        - Unencrypted PII transfers
        - Cross-border without mechanism
        - Third party without DPA contract
        """
        for flow in self:
            flow.compliance_gap = (
                (flow.contains_pii and not flow.lawful_basis_id)
                or (flow.contains_pii and not flow.is_encrypted)
                or (flow.is_cross_border and not flow.transfer_mechanism)
                or (flow.involves_third_party and not flow.dpa_contract_in_place)
            )

    @api.depends("status", "compliance_gap")
    def _compute_color(self):
        """Set color based on status and compliance."""
        for flow in self:
            if flow.status == "non_compliant" or flow.compliance_gap:
                flow.color = 1  # Red
            elif flow.status == "pending_review":
                flow.color = 3  # Yellow
            elif flow.status == "active":
                flow.color = 10  # Green
            else:
                flow.color = 0  # Gray

    @api.constrains("source_asset_id", "target_asset_id")
    def _check_source_target(self):
        """Ensure source and target are different."""
        for flow in self:
            if flow.source_asset_id == flow.target_asset_id:
                raise ValidationError(
                    "Source and target assets must be different."
                )

    def action_mark_compliant(self):
        """Mark data flow as compliant."""
        self.ensure_one()
        self.write({
            "status": "active",
            "last_review_date": fields.Date.today(),
        })

    def action_flag_non_compliant(self):
        """Flag data flow as non-compliant."""
        self.ensure_one()
        self.status = "non_compliant"
