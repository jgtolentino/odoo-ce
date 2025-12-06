# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Security Data Category Model
============================

Defines data categories for PH DPA compliance tracking:
- Personal Information
- Sensitive Personal Information
- Privileged Information
- Financial Data
"""
from odoo import api, fields, models


class SecurityDataCategory(models.Model):
    """
    Data category classification for PH DPA compliance.

    Categories follow the Philippines Data Privacy Act definitions for
    personal information, sensitive personal information, and privileged
    information.

    Attributes:
        _name: Model technical name
        _description: Human-readable model description
        _order: Default ordering for lists
    """

    _name = "security.data.category"
    _description = "Data Category"
    _order = "sequence, name"
    _parent_name = "parent_id"
    _parent_store = True

    name = fields.Char(
        string="Category Name",
        required=True,
        help="Name of the data category",
    )
    code = fields.Char(
        string="Code",
        required=True,
        help="Short code for the category (e.g., PII, SPI)",
    )
    description = fields.Text(
        string="Description",
        help="Detailed description of what data this category includes",
    )
    sensitivity_level = fields.Selection(
        [
            ("public", "Public"),
            ("internal", "Internal"),
            ("confidential", "Confidential"),
            ("restricted", "Restricted"),
        ],
        string="Sensitivity Level",
        default="internal",
        required=True,
        help="Data sensitivity classification",
    )
    dpa_classification = fields.Selection(
        [
            ("non_personal", "Non-Personal Data"),
            ("personal", "Personal Information"),
            ("sensitive_personal", "Sensitive Personal Information"),
            ("privileged", "Privileged Information"),
        ],
        string="DPA Classification",
        default="non_personal",
        required=True,
        help="Classification under PH Data Privacy Act",
    )
    requires_consent = fields.Boolean(
        string="Requires Explicit Consent",
        default=False,
        help="Whether processing requires explicit consent under DPA",
    )
    retention_period = fields.Integer(
        string="Default Retention (Days)",
        help="Default retention period in days (0 = indefinite)",
    )
    parent_id = fields.Many2one(
        "security.data.category",
        string="Parent Category",
        index=True,
        ondelete="cascade",
        help="Parent category for hierarchical classification",
    )
    parent_path = fields.Char(
        index=True,
        unaccent=False,
    )
    child_ids = fields.One2many(
        "security.data.category",
        "parent_id",
        string="Subcategories",
        help="Child categories",
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
        help="Color for display in views",
    )
    examples = fields.Text(
        string="Examples",
        help="Examples of data that fall under this category",
    )

    _sql_constraints = [
        (
            "code_unique",
            "UNIQUE(code)",
            "Data category code must be unique!",
        ),
    ]

    @api.depends("name", "parent_id.complete_name")
    def _compute_complete_name(self):
        """Compute complete hierarchical name."""
        for category in self:
            if category.parent_id:
                category.complete_name = (
                    f"{category.parent_id.complete_name} / {category.name}"
                )
            else:
                category.complete_name = category.name

    complete_name = fields.Char(
        string="Complete Name",
        compute="_compute_complete_name",
        recursive=True,
        store=True,
    )
