# -*- coding: utf-8 -*-
from odoo import api, fields, models


class IpaiBlock(models.Model):
    """
    Block - Modular content unit within a page.

    Notion-style blocks including:
    - Text (paragraph, headings)
    - Todo/checkbox
    - Lists (bulleted, numbered)
    - Quote, callout, divider
    - Code
    - Embed (images, videos, iframes)
    - Database view (future)
    """

    _name = "ipai.block"
    _description = "IPAI Block"
    _order = "page_id, sequence"

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------
    page_id = fields.Many2one(
        "ipai.page",
        string="Page",
        required=True,
        ondelete="cascade",
        index=True,
    )
    workspace_id = fields.Many2one(
        related="page_id.workspace_id",
        string="Workspace",
        store=True,
        index=True,
    )

    # Block type
    block_type = fields.Selection(
        [
            # Text blocks
            ("paragraph", "Paragraph"),
            ("heading_1", "Heading 1"),
            ("heading_2", "Heading 2"),
            ("heading_3", "Heading 3"),
            # List blocks
            ("bulleted_list", "Bulleted List"),
            ("numbered_list", "Numbered List"),
            ("todo", "To-do"),
            # Rich blocks
            ("quote", "Quote"),
            ("callout", "Callout"),
            ("divider", "Divider"),
            ("code", "Code"),
            # Media blocks
            ("image", "Image"),
            ("video", "Video"),
            ("embed", "Embed"),
            ("file", "File"),
            # Advanced blocks (future)
            ("database_view", "Database View"),
            ("table", "Table"),
            ("toggle", "Toggle"),
            ("synced_block", "Synced Block"),
        ],
        string="Block Type",
        default="paragraph",
        required=True,
    )

    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )

    # Content
    content = fields.Text(
        string="Content",
        help="Plain text content of the block",
    )
    content_html = fields.Html(
        string="Rich Content",
        sanitize=True,
        strip_style=False,
        help="Rich text content with formatting",
    )

    # Properties (JSON for flexibility)
    properties = fields.Text(
        string="Properties (JSON)",
        default="{}",
        help="Block-specific properties in JSON format",
    )

    # Todo specific
    is_checked = fields.Boolean(
        string="Checked",
        default=False,
        help="For todo blocks: completion status",
    )

    # Code specific
    code_language = fields.Char(
        string="Language",
        help="Programming language for code blocks",
    )

    # Embed/Media specific
    embed_url = fields.Char(
        string="Embed URL",
        help="URL for embed/video blocks",
    )
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="Attachment",
        help="File attachment for image/file blocks",
    )

    # Callout specific
    callout_icon = fields.Char(
        string="Callout Icon",
        default="💡",
    )
    callout_color = fields.Selection(
        [
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
        ],
        string="Callout Color",
        default="default",
    )

    # Database view specific (for future ipai_workspace_db)
    database_model_name = fields.Char(
        string="Database Model",
        help="Odoo model name for database_view blocks",
    )
    database_view_type = fields.Selection(
        [
            ("list", "List"),
            ("kanban", "Kanban"),
            ("calendar", "Calendar"),
            ("gallery", "Gallery"),
            ("timeline", "Timeline"),
        ],
        string="View Type",
        default="list",
    )
    database_filter = fields.Text(
        string="Filter (JSON)",
        help="Saved filters for the database view",
    )

    # Nested blocks (for toggle, synced blocks)
    parent_block_id = fields.Many2one(
        "ipai.block",
        string="Parent Block",
        ondelete="cascade",
        index=True,
    )
    child_block_ids = fields.One2many(
        "ipai.block",
        "parent_block_id",
        string="Child Blocks",
    )

    # -------------------------------------------------------------------------
    # COMPUTED FIELDS
    # -------------------------------------------------------------------------
    display_preview = fields.Char(
        string="Preview",
        compute="_compute_display_preview",
    )

    @api.depends("block_type", "content")
    def _compute_display_preview(self):
        """Generate preview text for list views."""
        for block in self:
            type_label = dict(self._fields["block_type"].selection).get(
                block.block_type, block.block_type
            )
            content_preview = (block.content or "")[:50]
            if len(block.content or "") > 50:
                content_preview += "..."
            block.display_preview = f"[{type_label}] {content_preview}"

    # -------------------------------------------------------------------------
    # API METHODS
    # -------------------------------------------------------------------------
    def to_json(self):
        """Convert block to JSON representation for block editor."""
        self.ensure_one()
        return {
            "id": self.id,
            "type": self.block_type,
            "sequence": self.sequence,
            "content": self.content,
            "content_html": self.content_html,
            "properties": self.properties,
            "is_checked": self.is_checked,
            "code_language": self.code_language,
            "embed_url": self.embed_url,
            "callout_icon": self.callout_icon,
            "callout_color": self.callout_color,
            "children": [child.to_json() for child in self.child_block_ids],
        }

    @api.model
    def from_json(self, data, page_id, parent_block_id=False, sequence=10):
        """Create block from JSON representation."""
        vals = {
            "page_id": page_id,
            "parent_block_id": parent_block_id,
            "sequence": sequence,
            "block_type": data.get("type", "paragraph"),
            "content": data.get("content"),
            "content_html": data.get("content_html"),
            "properties": data.get("properties", "{}"),
            "is_checked": data.get("is_checked", False),
            "code_language": data.get("code_language"),
            "embed_url": data.get("embed_url"),
            "callout_icon": data.get("callout_icon", "💡"),
            "callout_color": data.get("callout_color", "default"),
        }
        block = self.create(vals)

        # Create children recursively
        for i, child_data in enumerate(data.get("children", [])):
            self.from_json(child_data, page_id, block.id, i * 10)

        return block

    # -------------------------------------------------------------------------
    # ACTION METHODS
    # -------------------------------------------------------------------------
    def action_toggle_todo(self):
        """Toggle todo block completion."""
        for block in self.filtered(lambda b: b.block_type == "todo"):
            block.is_checked = not block.is_checked

    def action_move_up(self):
        """Move block up in sequence."""
        self.ensure_one()
        prev_block = self.search(
            [
                ("page_id", "=", self.page_id.id),
                ("parent_block_id", "=", self.parent_block_id.id),
                ("sequence", "<", self.sequence),
            ],
            order="sequence desc",
            limit=1,
        )
        if prev_block:
            prev_seq = prev_block.sequence
            prev_block.sequence = self.sequence
            self.sequence = prev_seq

    def action_move_down(self):
        """Move block down in sequence."""
        self.ensure_one()
        next_block = self.search(
            [
                ("page_id", "=", self.page_id.id),
                ("parent_block_id", "=", self.parent_block_id.id),
                ("sequence", ">", self.sequence),
            ],
            order="sequence asc",
            limit=1,
        )
        if next_block:
            next_seq = next_block.sequence
            next_block.sequence = self.sequence
            self.sequence = next_seq
