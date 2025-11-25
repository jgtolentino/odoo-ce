# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class IpaiPageTemplate(models.Model):
    """
    Page Template - Reusable page structure for quick creation.

    Templates can be:
    - Workspace-specific or global
    - Include pre-defined blocks
    - Auto-populate with variables
    """
    _name = "ipai.page.template"
    _description = "IPAI Page Template"
    _order = "sequence, name"

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------
    name = fields.Char(
        string="Template Name",
        required=True,
        index=True,
    )
    description = fields.Text(
        string="Description",
        help="Brief description of when to use this template",
    )
    icon = fields.Char(
        string="Icon",
        default="📋",
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )

    # Scope
    is_global = fields.Boolean(
        string="Global Template",
        default=False,
        help="Available across all workspaces",
    )
    workspace_id = fields.Many2one(
        "ipai.workspace",
        string="Workspace",
        help="Limit template to specific workspace (if not global)",
    )

    # Template content
    default_title = fields.Char(
        string="Default Page Title",
        default=lambda self: _("New Page"),
    )
    content_html = fields.Html(
        string="Content (HTML)",
        sanitize=True,
        help="HTML content for simple templates",
    )
    content_json = fields.Text(
        string="Content (JSON)",
        help="Block-based content in JSON format",
    )

    # Predefined blocks
    template_block_ids = fields.One2many(
        "ipai.template.block",
        "template_id",
        string="Template Blocks",
    )

    # Categories
    category = fields.Selection([
        ("general", "General"),
        ("meeting", "Meetings"),
        ("project", "Projects"),
        ("documentation", "Documentation"),
        ("planning", "Planning"),
        ("personal", "Personal"),
    ], string="Category", default="general")

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------
    def action_create_page(self, workspace_id, parent_id=False):
        """
        Create a new page from this template.

        :param workspace_id: int - Target workspace ID
        :param parent_id: int - Optional parent page ID
        :return: ipai.page record
        """
        self.ensure_one()
        Page = self.env["ipai.page"]
        Block = self.env["ipai.block"]

        # Create the page
        page = Page.create({
            "name": self.default_title,
            "icon": self.icon,
            "workspace_id": workspace_id,
            "parent_id": parent_id,
            "template_id": self.id,
            "content_html": self.content_html,
            "content_json": self.content_json,
        })

        # Copy template blocks
        for tblock in self.template_block_ids.sorted("sequence"):
            Block.create({
                "page_id": page.id,
                "block_type": tblock.block_type,
                "sequence": tblock.sequence,
                "content": tblock.content,
                "content_html": tblock.content_html,
                "properties": tblock.properties,
                "callout_icon": tblock.callout_icon,
                "callout_color": tblock.callout_color,
                "code_language": tblock.code_language,
            })

        return page

    def action_preview(self):
        """Open preview of template."""
        self.ensure_one()
        return {
            "name": _("Template Preview: %s") % self.name,
            "type": "ir.actions.act_window",
            "res_model": "ipai.page.template",
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }


class IpaiTemplateBlock(models.Model):
    """Template Block - Block definition within a template."""
    _name = "ipai.template.block"
    _description = "IPAI Template Block"
    _order = "sequence"

    template_id = fields.Many2one(
        "ipai.page.template",
        string="Template",
        required=True,
        ondelete="cascade",
    )

    block_type = fields.Selection([
        ("paragraph", "Paragraph"),
        ("heading_1", "Heading 1"),
        ("heading_2", "Heading 2"),
        ("heading_3", "Heading 3"),
        ("bulleted_list", "Bulleted List"),
        ("numbered_list", "Numbered List"),
        ("todo", "To-do"),
        ("quote", "Quote"),
        ("callout", "Callout"),
        ("divider", "Divider"),
        ("code", "Code"),
    ], string="Block Type", default="paragraph", required=True)

    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )
    content = fields.Text(
        string="Content",
    )
    content_html = fields.Html(
        string="Rich Content",
        sanitize=True,
    )
    properties = fields.Text(
        string="Properties (JSON)",
        default="{}",
    )
    callout_icon = fields.Char(
        string="Callout Icon",
        default="💡",
    )
    callout_color = fields.Selection([
        ("default", "Default"),
        ("gray", "Gray"),
        ("brown", "Brown"),
        ("orange", "Orange"),
        ("yellow", "Yellow"),
        ("green", "Green"),
        ("blue", "Blue"),
        ("purple", "Purple"),
        ("pink", "Pink"),
        ("red", "Red"),
    ], string="Callout Color", default="default")
    code_language = fields.Char(
        string="Language",
    )
