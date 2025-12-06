# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
"""
Project Brief model for creative/agency workflows.

This model captures structured inputs for creative and strategic work
before production begins.
"""

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProjectBrief(models.Model):
    """
    A structured brief for creative/agency projects.

    Captures objectives, target audience, key messages, deliverables,
    budget, and deadline linked to a standard Odoo project.
    """

    _name = "project.brief"
    _description = "Project Brief"
    _order = "create_date desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------
    name = fields.Char(
        string="Brief Title",
        required=True,
        tracking=True,
        help="Short internal title for this brief.",
    )

    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        required=True,
        ondelete="cascade",
        tracking=True,
        help="Linked project in Odoo.",
    )

    client_id = fields.Many2one(
        comodel_name="res.partner",
        string="Client",
        required=True,
        domain=[("is_company", "=", True)],
        tracking=True,
        help="Client company for this brief.",
    )

    brand_name = fields.Char(
        string="Brand",
        help="Brand involved in this brief.",
    )

    objective = fields.Text(
        string="Objective",
        help="Business/communication objective of the project.",
    )

    target_audience = fields.Text(
        string="Target Audience",
    )

    key_message = fields.Text(
        string="Key Message",
    )

    deliverables = fields.Text(
        string="Deliverables",
    )

    budget = fields.Monetary(
        string="Estimated Budget",
        currency_field="company_currency_id",
        tracking=True,
    )

    deadline = fields.Date(
        string="Deadline",
        tracking=True,
    )

    status = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("in_review", "In Review"),
            ("approved", "Approved"),
            ("on_hold", "On Hold"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
        tracking=True,
    )

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=True,
    )

    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Company Currency",
        related="company_id.currency_id",
        readonly=True,
    )

    is_locked = fields.Boolean(
        string="Locked",
        help="Locked briefs can no longer be edited, only read.",
        default=False,
    )

    # Computed fields
    days_until_deadline = fields.Integer(
        string="Days Until Deadline",
        compute="_compute_days_until_deadline",
        store=False,
    )

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------
    @api.depends("deadline")
    def _compute_days_until_deadline(self):
        """Compute the number of days until the deadline."""
        today = fields.Date.today()
        for rec in self:
            if rec.deadline:
                delta = rec.deadline - today
                rec.days_until_deadline = delta.days
            else:
                rec.days_until_deadline = 0

    # -------------------------------------------------------------------------
    # CONSTRAINTS
    # -------------------------------------------------------------------------
    @api.constrains("deadline")
    def _check_deadline(self):
        """Ensure deadline is not in the past when creating/updating."""
        for rec in self:
            if rec.deadline and rec.deadline < fields.Date.today():
                # Only enforce on creation or when explicitly changing deadline
                if self.env.context.get("allow_past_deadline"):
                    continue
                raise ValidationError(
                    _("Deadline cannot be in the past.")
                )

    @api.constrains("budget")
    def _check_budget(self):
        """Ensure budget is non-negative."""
        for rec in self:
            if rec.budget and rec.budget < 0:
                raise ValidationError(
                    _("Budget cannot be negative.")
                )

    # -------------------------------------------------------------------------
    # CRUD OVERRIDES
    # -------------------------------------------------------------------------
    def write(self, vals):
        """
        Protect locked briefs from being edited except by administrators.

        Raises ValidationError if a non-admin user attempts to modify
        a locked brief.
        """
        for rec in self:
            if rec.is_locked and not self.env.user.has_group("base.group_system"):
                # Allow unlocking by admins
                if vals.get("is_locked") is False and len(vals) == 1:
                    continue
                raise ValidationError(
                    _("You cannot edit a locked brief. "
                      "Please contact an administrator.")
                )
        return super().write(vals)

    def unlink(self):
        """Prevent deletion of approved briefs."""
        for rec in self:
            if rec.status == "approved":
                raise ValidationError(
                    _("Cannot delete an approved brief. "
                      "Please cancel it first.")
                )
        return super().unlink()

    # -------------------------------------------------------------------------
    # ACTION METHODS
    # -------------------------------------------------------------------------
    def action_mark_in_review(self):
        """Move brief to 'In Review' status."""
        for rec in self:
            if rec.status not in ("draft", "on_hold"):
                raise ValidationError(
                    _("Only draft or on-hold briefs can be sent for review.")
                )
            rec.status = "in_review"

    def action_approve(self):
        """Approve the brief and lock it."""
        for rec in self:
            if rec.status not in ("in_review", "on_hold"):
                raise ValidationError(
                    _("Only briefs in review or on hold can be approved.")
                )
            rec.write({
                "status": "approved",
                "is_locked": True,
            })

    def action_hold(self):
        """Put brief on hold."""
        for rec in self:
            if rec.status == "cancelled":
                raise ValidationError(
                    _("Cancelled briefs cannot be put on hold.")
                )
            rec.status = "on_hold"

    def action_cancel(self):
        """Cancel the brief."""
        for rec in self:
            if rec.status == "approved":
                raise ValidationError(
                    _("Approved briefs cannot be cancelled directly. "
                      "Please unlock first.")
                )
            rec.status = "cancelled"

    def action_unlock(self):
        """Unlock a locked brief (admin only)."""
        self.ensure_one()
        if not self.env.user.has_group("base.group_system"):
            raise ValidationError(
                _("Only administrators can unlock briefs.")
            )
        self.is_locked = False

    def action_reset_to_draft(self):
        """Reset a cancelled or on-hold brief back to draft."""
        for rec in self:
            if rec.status not in ("cancelled", "on_hold"):
                raise ValidationError(
                    _("Only cancelled or on-hold briefs can be reset to draft.")
                )
            rec.write({
                "status": "draft",
                "is_locked": False,
            })
