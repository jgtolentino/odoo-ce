# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class IpaiWorkspace(models.Model):
    """
    Workspace - Top-level container for pages and databases.

    Implements Notion-style workspace with:
    - Privacy controls (private/shared/public)
    - Member management with roles
    - Hierarchical page organization
    """
    _name = "ipai.workspace"
    _description = "IPAI Workspace"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------
    name = fields.Char(
        string="Workspace Name",
        required=True,
        tracking=True,
        index=True,
    )
    description = fields.Text(
        string="Description",
        help="Brief description of the workspace purpose",
    )
    icon = fields.Char(
        string="Icon",
        default="📁",
        help="Emoji or icon code for the workspace",
    )
    cover_image = fields.Binary(
        string="Cover Image",
        attachment=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Display order in workspace list",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
    )

    # Privacy & Access
    privacy = fields.Selection([
        ("private", "Private"),
        ("shared", "Shared with Members"),
        ("public", "Public (Read-only)"),
    ], string="Privacy", default="shared", required=True, tracking=True)

    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        required=True,
        default=lambda self: self.env.user,
        tracking=True,
        index=True,
    )
    member_ids = fields.Many2many(
        "res.users",
        "ipai_workspace_member_rel",
        "workspace_id",
        "user_id",
        string="Members",
        help="Users with access to this workspace",
    )

    # Relations
    page_ids = fields.One2many(
        "ipai.page",
        "workspace_id",
        string="Pages",
    )
    root_page_ids = fields.One2many(
        "ipai.page",
        "workspace_id",
        string="Root Pages",
        domain=[("parent_id", "=", False)],
    )

    # Computed
    page_count = fields.Integer(
        string="Page Count",
        compute="_compute_page_count",
        store=True,
    )
    member_count = fields.Integer(
        string="Member Count",
        compute="_compute_member_count",
        store=True,
    )

    # -------------------------------------------------------------------------
    # CONSTRAINTS
    # -------------------------------------------------------------------------
    _sql_constraints = [
        (
            "name_owner_unique",
            "unique(name, owner_id)",
            "Workspace name must be unique per owner!"
        ),
    ]

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------
    @api.depends("page_ids")
    def _compute_page_count(self):
        for workspace in self:
            workspace.page_count = len(workspace.page_ids)

    @api.depends("member_ids")
    def _compute_member_count(self):
        for workspace in self:
            workspace.member_count = len(workspace.member_ids)

    # -------------------------------------------------------------------------
    # CRUD OVERRIDES
    # -------------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        """Ensure owner is always a member."""
        for vals in vals_list:
            owner_id = vals.get("owner_id", self.env.user.id)
            member_ids = vals.get("member_ids", [(6, 0, [])])
            # Add owner to members if not already present
            if isinstance(member_ids, list) and member_ids:
                if member_ids[0][0] == 6:  # Replace all
                    if owner_id not in member_ids[0][2]:
                        member_ids[0][2].append(owner_id)
            else:
                vals["member_ids"] = [(6, 0, [owner_id])]
        return super().create(vals_list)

    def write(self, vals):
        """Prevent removing owner from members."""
        result = super().write(vals)
        for workspace in self:
            if workspace.owner_id not in workspace.member_ids:
                workspace.member_ids = [(4, workspace.owner_id.id)]
        return result

    # -------------------------------------------------------------------------
    # ACCESS METHODS
    # -------------------------------------------------------------------------
    def _check_access(self, user=None, mode="read"):
        """
        Check if user has access to workspace.

        :param user: res.users record (default: current user)
        :param mode: 'read', 'write', or 'owner'
        :return: True if access granted
        """
        self.ensure_one()
        user = user or self.env.user

        if user.has_group("base.group_system"):
            return True

        if mode == "owner":
            return user == self.owner_id

        if self.privacy == "public":
            return True

        if self.privacy == "private":
            return user == self.owner_id

        # Shared workspace
        return user in self.member_ids

    def action_add_member(self, user_id):
        """Add a member to the workspace."""
        self.ensure_one()
        if not self._check_access(mode="owner"):
            raise ValidationError(_("Only the owner can add members."))
        self.member_ids = [(4, user_id)]

    def action_remove_member(self, user_id):
        """Remove a member from the workspace."""
        self.ensure_one()
        if not self._check_access(mode="owner"):
            raise ValidationError(_("Only the owner can remove members."))
        if user_id == self.owner_id.id:
            raise ValidationError(_("Cannot remove the workspace owner."))
        self.member_ids = [(3, user_id)]

    # -------------------------------------------------------------------------
    # ACTION METHODS
    # -------------------------------------------------------------------------
    def action_view_pages(self):
        """Open the page tree view for this workspace."""
        self.ensure_one()
        return {
            "name": _("Pages in %s") % self.name,
            "type": "ir.actions.act_window",
            "res_model": "ipai.page",
            "view_mode": "tree,form,kanban",
            "domain": [("workspace_id", "=", self.id)],
            "context": {
                "default_workspace_id": self.id,
                "search_default_filter_root": True,
            },
        }

    def action_create_page(self):
        """Create a new root page in this workspace."""
        self.ensure_one()
        return {
            "name": _("New Page"),
            "type": "ir.actions.act_window",
            "res_model": "ipai.page",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_workspace_id": self.id,
            },
        }
