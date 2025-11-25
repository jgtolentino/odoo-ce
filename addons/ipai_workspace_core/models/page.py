# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class IpaiPage(models.Model):
    """
    Page - Notion-style document with hierarchical structure.

    Supports:
    - Parent/child hierarchy (unlimited depth)
    - Block-based content
    - Templates
    - Backlinks
    - Database linking (future ipai_workspace_db module)
    """
    _name = "ipai.page"
    _description = "IPAI Page"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = "display_name"

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------
    name = fields.Char(
        string="Title",
        required=True,
        tracking=True,
        index=True,
        default=lambda self: _("Untitled"),
    )
    display_name = fields.Char(
        string="Display Name",
        compute="_compute_display_name",
        store=True,
    )
    icon = fields.Char(
        string="Icon",
        default="📄",
        help="Emoji or icon for the page",
    )
    cover_image = fields.Binary(
        string="Cover Image",
        attachment=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
        tracking=True,
    )

    # Content
    content_html = fields.Html(
        string="Content (HTML)",
        sanitize=True,
        sanitize_tags=True,
        sanitize_attributes=True,
        strip_style=False,
        strip_classes=False,
        help="Rich text content (basic editor fallback)",
    )
    content_json = fields.Text(
        string="Content (JSON)",
        help="Block-based content in JSON format for advanced editor",
    )

    # Hierarchy
    workspace_id = fields.Many2one(
        "ipai.workspace",
        string="Workspace",
        required=True,
        ondelete="cascade",
        tracking=True,
        index=True,
    )
    parent_id = fields.Many2one(
        "ipai.page",
        string="Parent Page",
        ondelete="cascade",
        index=True,
        domain="[('workspace_id', '=', workspace_id)]",
    )
    parent_path = fields.Char(
        string="Parent Path",
        index=True,
    )
    child_ids = fields.One2many(
        "ipai.page",
        "parent_id",
        string="Sub-pages",
    )
    child_count = fields.Integer(
        string="Sub-page Count",
        compute="_compute_child_count",
        store=True,
    )
    depth = fields.Integer(
        string="Depth",
        compute="_compute_depth",
        store=True,
    )

    # Blocks
    block_ids = fields.One2many(
        "ipai.block",
        "page_id",
        string="Blocks",
    )
    block_count = fields.Integer(
        string="Block Count",
        compute="_compute_block_count",
        store=True,
    )

    # Backlinks
    backlink_ids = fields.One2many(
        "ipai.backlink",
        "target_page_id",
        string="Backlinks",
        help="Pages that reference this page",
    )
    outgoing_link_ids = fields.One2many(
        "ipai.backlink",
        "source_page_id",
        string="Outgoing Links",
        help="Pages referenced by this page",
    )

    # Template
    is_template = fields.Boolean(
        string="Is Template",
        default=False,
        help="Mark this page as a reusable template",
    )
    template_id = fields.Many2one(
        "ipai.page.template",
        string="Created From Template",
        help="The template this page was created from",
    )

    # Database (for future ipai_workspace_db module)
    is_database = fields.Boolean(
        string="Is Database",
        default=False,
        help="This page represents a database view",
    )
    database_model = fields.Char(
        string="Database Model",
        help="Odoo model name if this page is a database",
    )

    # Metadata
    created_by_id = fields.Many2one(
        "res.users",
        string="Created By",
        default=lambda self: self.env.user,
        readonly=True,
    )
    last_edited_by_id = fields.Many2one(
        "res.users",
        string="Last Edited By",
        readonly=True,
    )
    last_edited_date = fields.Datetime(
        string="Last Edited",
        readonly=True,
    )

    # Full-text search
    full_text = fields.Text(
        string="Full Text",
        compute="_compute_full_text",
        store=True,
        help="Concatenated text for full-text search",
    )

    # -------------------------------------------------------------------------
    # CONSTRAINTS
    # -------------------------------------------------------------------------
    @api.constrains("parent_id")
    def _check_parent_id(self):
        """Prevent circular references."""
        if not self._check_recursion():
            raise ValidationError(_("Error! You cannot create recursive pages."))

    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------
    @api.depends("name", "icon")
    def _compute_display_name(self):
        for page in self:
            icon = page.icon or "📄"
            page.display_name = f"{icon} {page.name}"

    @api.depends("child_ids")
    def _compute_child_count(self):
        for page in self:
            page.child_count = len(page.child_ids)

    @api.depends("parent_path")
    def _compute_depth(self):
        for page in self:
            if page.parent_path:
                page.depth = page.parent_path.count("/") - 1
            else:
                page.depth = 0

    @api.depends("block_ids")
    def _compute_block_count(self):
        for page in self:
            page.block_count = len(page.block_ids)

    @api.depends("name", "content_html", "block_ids.content")
    def _compute_full_text(self):
        """Build full-text search index from page content."""
        for page in self:
            parts = [page.name or ""]

            # Add HTML content (strip tags)
            if page.content_html:
                text = re.sub(r"<[^>]+>", " ", page.content_html)
                parts.append(text)

            # Add block content
            for block in page.block_ids:
                if block.content:
                    parts.append(block.content)

            page.full_text = " ".join(parts)

    # -------------------------------------------------------------------------
    # CRUD OVERRIDES
    # -------------------------------------------------------------------------
    def write(self, vals):
        """Track last editor and parse backlinks."""
        vals["last_edited_by_id"] = self.env.user.id
        vals["last_edited_date"] = fields.Datetime.now()
        result = super().write(vals)

        # Re-parse backlinks if content changed
        if "content_html" in vals or "content_json" in vals:
            self._parse_backlinks()

        return result

    def unlink(self):
        """Clean up backlinks before deletion."""
        self.env["ipai.backlink"].search([
            "|",
            ("source_page_id", "in", self.ids),
            ("target_page_id", "in", self.ids),
        ]).unlink()
        return super().unlink()

    # -------------------------------------------------------------------------
    # BACKLINK METHODS
    # -------------------------------------------------------------------------
    def _parse_backlinks(self):
        """
        Parse content for [[page]] references and create/update backlinks.

        Supports:
        - [[Page Title]] - link by title
        - [[id:123]] - link by ID
        """
        Backlink = self.env["ipai.backlink"]
        page_pattern = re.compile(r"\[\[([^\]]+)\]\]")

        for page in self:
            # Remove existing outgoing links
            page.outgoing_link_ids.unlink()

            # Parse content for links
            content = (page.content_html or "") + (page.content_json or "")
            matches = page_pattern.findall(content)

            for match in matches:
                target = None

                # Check for ID reference
                if match.startswith("id:"):
                    try:
                        target_id = int(match[3:])
                        target = self.browse(target_id).exists()
                    except (ValueError, TypeError):
                        continue
                else:
                    # Search by title in same workspace
                    target = self.search([
                        ("workspace_id", "=", page.workspace_id.id),
                        ("name", "=ilike", match),
                        ("id", "!=", page.id),
                    ], limit=1)

                if target:
                    Backlink.create({
                        "source_page_id": page.id,
                        "target_page_id": target.id,
                        "link_text": match,
                    })

    # -------------------------------------------------------------------------
    # ACTION METHODS
    # -------------------------------------------------------------------------
    def action_view_subpages(self):
        """View all sub-pages of this page."""
        self.ensure_one()
        return {
            "name": _("Sub-pages of %s") % self.name,
            "type": "ir.actions.act_window",
            "res_model": "ipai.page",
            "view_mode": "tree,form",
            "domain": [("parent_id", "=", self.id)],
            "context": {
                "default_workspace_id": self.workspace_id.id,
                "default_parent_id": self.id,
            },
        }

    def action_create_subpage(self):
        """Create a new sub-page under this page."""
        self.ensure_one()
        return {
            "name": _("New Sub-page"),
            "type": "ir.actions.act_window",
            "res_model": "ipai.page",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_workspace_id": self.workspace_id.id,
                "default_parent_id": self.id,
            },
        }

    def action_duplicate_as_template(self):
        """Save this page as a reusable template."""
        self.ensure_one()
        return {
            "name": _("Save as Template"),
            "type": "ir.actions.act_window",
            "res_model": "ipai.page.template",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_name": f"{self.name} Template",
                "default_workspace_id": self.workspace_id.id,
                "default_content_html": self.content_html,
                "default_content_json": self.content_json,
                "default_icon": self.icon,
            },
        }

    def action_view_backlinks(self):
        """View all pages that link to this page."""
        self.ensure_one()
        source_ids = self.backlink_ids.mapped("source_page_id").ids
        return {
            "name": _("Pages linking to %s") % self.name,
            "type": "ir.actions.act_window",
            "res_model": "ipai.page",
            "view_mode": "tree,form",
            "domain": [("id", "in", source_ids)],
        }

    # -------------------------------------------------------------------------
    # UTILITY METHODS
    # -------------------------------------------------------------------------
    def get_breadcrumb(self):
        """Return list of ancestor pages for breadcrumb navigation."""
        self.ensure_one()
        breadcrumb = []
        page = self
        while page:
            breadcrumb.insert(0, {
                "id": page.id,
                "name": page.name,
                "icon": page.icon,
            })
            page = page.parent_id
        return breadcrumb

    def get_tree_path(self):
        """Return full path string like 'Workspace / Parent / Page'."""
        self.ensure_one()
        parts = [p["name"] for p in self.get_breadcrumb()]
        return " / ".join(parts)
