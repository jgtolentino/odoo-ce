# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class WorkspaceController(http.Controller):
    """
    REST API endpoints for IPAI Workspace.

    Provides JSON API for:
    - Page content (for external editors)
    - Block operations
    - Backlink queries
    - Graph data
    """

    # -------------------------------------------------------------------------
    # PAGE ENDPOINTS
    # -------------------------------------------------------------------------

    @http.route("/workspace/api/page/<int:page_id>", type="json", auth="user")
    def get_page(self, page_id):
        """
        Get page data including blocks.

        Returns:
            dict: Page data with blocks as JSON
        """
        page = request.env["ipai.page"].browse(page_id)
        if not page.exists():
            return {"error": "Page not found", "code": 404}

        return {
            "id": page.id,
            "name": page.name,
            "icon": page.icon,
            "workspace_id": page.workspace_id.id,
            "workspace_name": page.workspace_id.name,
            "parent_id": page.parent_id.id if page.parent_id else None,
            "content_html": page.content_html,
            "content_json": page.content_json,
            "breadcrumb": page.get_breadcrumb(),
            "blocks": [block.to_json() for block in page.block_ids.sorted("sequence")],
            "backlinks": request.env["ipai.backlink"].get_backlinks_for_page(page_id),
            "created_by": page.created_by_id.name,
            "last_edited_by": (
                page.last_edited_by_id.name if page.last_edited_by_id else None
            ),
            "last_edited_date": (
                page.last_edited_date.isoformat() if page.last_edited_date else None
            ),
        }

    @http.route(
        "/workspace/api/page/<int:page_id>/save",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def save_page(self, page_id, **kwargs):
        """
        Save page content.

        Args:
            page_id: Page ID
            content_html: HTML content (optional)
            content_json: JSON content (optional)
            blocks: List of block data (optional)

        Returns:
            dict: Updated page data
        """
        page = request.env["ipai.page"].browse(page_id)
        if not page.exists():
            return {"error": "Page not found", "code": 404}

        vals = {}
        if "content_html" in kwargs:
            vals["content_html"] = kwargs["content_html"]
        if "content_json" in kwargs:
            vals["content_json"] = kwargs["content_json"]
        if "name" in kwargs:
            vals["name"] = kwargs["name"]
        if "icon" in kwargs:
            vals["icon"] = kwargs["icon"]

        if vals:
            page.write(vals)

        # Handle blocks if provided
        if "blocks" in kwargs:
            # Clear existing blocks and recreate
            page.block_ids.unlink()
            Block = request.env["ipai.block"]
            for i, block_data in enumerate(kwargs["blocks"]):
                Block.from_json(block_data, page.id, sequence=i * 10)

        return {"success": True, "page_id": page.id}

    # -------------------------------------------------------------------------
    # BLOCK ENDPOINTS
    # -------------------------------------------------------------------------

    @http.route(
        "/workspace/api/block/create", type="json", auth="user", methods=["POST"]
    )
    def create_block(
        self, page_id, block_type="paragraph", content=None, sequence=None, **kwargs
    ):
        """
        Create a new block in a page.

        Args:
            page_id: Target page ID
            block_type: Type of block
            content: Block content
            sequence: Position in page

        Returns:
            dict: Created block data
        """
        page = request.env["ipai.page"].browse(page_id)
        if not page.exists():
            return {"error": "Page not found", "code": 404}

        # Calculate sequence if not provided
        if sequence is None:
            max_seq = max([b.sequence for b in page.block_ids] or [0])
            sequence = max_seq + 10

        vals = {
            "page_id": page_id,
            "block_type": block_type,
            "content": content,
            "sequence": sequence,
        }
        vals.update(
            {
                k: v
                for k, v in kwargs.items()
                if k
                in [
                    "content_html",
                    "is_checked",
                    "code_language",
                    "embed_url",
                    "callout_icon",
                    "callout_color",
                    "properties",
                ]
            }
        )

        block = request.env["ipai.block"].create(vals)
        return block.to_json()

    @http.route(
        "/workspace/api/block/<int:block_id>",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def update_block(self, block_id, **kwargs):
        """
        Update an existing block.

        Args:
            block_id: Block ID
            **kwargs: Fields to update

        Returns:
            dict: Updated block data
        """
        block = request.env["ipai.block"].browse(block_id)
        if not block.exists():
            return {"error": "Block not found", "code": 404}

        allowed_fields = [
            "block_type",
            "content",
            "content_html",
            "sequence",
            "is_checked",
            "code_language",
            "embed_url",
            "callout_icon",
            "callout_color",
            "properties",
        ]
        vals = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if vals:
            block.write(vals)

        return block.to_json()

    @http.route(
        "/workspace/api/block/<int:block_id>/delete",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def delete_block(self, block_id):
        """Delete a block."""
        block = request.env["ipai.block"].browse(block_id)
        if not block.exists():
            return {"error": "Block not found", "code": 404}

        block.unlink()
        return {"success": True}

    @http.route(
        "/workspace/api/block/toggle/<int:block_id>",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def toggle_todo(self, block_id):
        """Toggle a todo block's checked state."""
        block = request.env["ipai.block"].browse(block_id)
        if not block.exists():
            return {"error": "Block not found", "code": 404}

        if block.block_type != "todo":
            return {"error": "Block is not a todo", "code": 400}

        block.action_toggle_todo()
        return {"success": True, "is_checked": block.is_checked}

    # -------------------------------------------------------------------------
    # WORKSPACE ENDPOINTS
    # -------------------------------------------------------------------------

    @http.route(
        "/workspace/api/workspace/<int:workspace_id>/pages", type="json", auth="user"
    )
    def get_workspace_pages(self, workspace_id):
        """
        Get all pages in a workspace as a tree structure.

        Returns:
            list: Hierarchical page structure
        """
        workspace = request.env["ipai.workspace"].browse(workspace_id)
        if not workspace.exists():
            return {"error": "Workspace not found", "code": 404}

        def build_tree(pages):
            result = []
            for page in pages:
                node = {
                    "id": page.id,
                    "name": page.name,
                    "icon": page.icon,
                    "child_count": page.child_count,
                    "children": build_tree(page.child_ids) if page.child_ids else [],
                }
                result.append(node)
            return result

        root_pages = workspace.root_page_ids.sorted("sequence")
        return build_tree(root_pages)

    @http.route(
        "/workspace/api/workspace/<int:workspace_id>/graph", type="json", auth="user"
    )
    def get_workspace_graph(self, workspace_id):
        """
        Get page relationship graph for visualization.

        Returns:
            dict: Nodes and edges for graph rendering
        """
        return request.env["ipai.backlink"].get_page_graph(workspace_id)

    # -------------------------------------------------------------------------
    # SEARCH ENDPOINTS
    # -------------------------------------------------------------------------

    @http.route("/workspace/api/search", type="json", auth="user")
    def search_pages(self, query, workspace_id=None, limit=20):
        """
        Full-text search across pages.

        Args:
            query: Search string
            workspace_id: Optional workspace filter
            limit: Max results

        Returns:
            list: Matching pages
        """
        domain = [("full_text", "ilike", query)]
        if workspace_id:
            domain.append(("workspace_id", "=", workspace_id))

        pages = request.env["ipai.page"].search(domain, limit=limit)
        return [
            {
                "id": page.id,
                "name": page.name,
                "icon": page.icon,
                "workspace_id": page.workspace_id.id,
                "workspace_name": page.workspace_id.name,
                "path": page.get_tree_path(),
            }
            for page in pages
        ]

    # -------------------------------------------------------------------------
    # TEMPLATE ENDPOINTS
    # -------------------------------------------------------------------------

    @http.route("/workspace/api/templates", type="json", auth="user")
    def get_templates(self, workspace_id=None, category=None):
        """
        Get available page templates.

        Args:
            workspace_id: Filter by workspace (also includes global)
            category: Filter by category

        Returns:
            list: Available templates
        """
        domain = [("active", "=", True)]

        if workspace_id:
            domain.append("|")
            domain.append(("is_global", "=", True))
            domain.append(("workspace_id", "=", workspace_id))
        else:
            domain.append(("is_global", "=", True))

        if category:
            domain.append(("category", "=", category))

        templates = request.env["ipai.page.template"].search(domain)
        return [
            {
                "id": t.id,
                "name": t.name,
                "icon": t.icon,
                "description": t.description,
                "category": t.category,
                "is_global": t.is_global,
            }
            for t in templates
        ]

    @http.route(
        "/workspace/api/template/<int:template_id>/create",
        type="json",
        auth="user",
        methods=["POST"],
    )
    def create_from_template(self, template_id, workspace_id, parent_id=None):
        """
        Create a new page from a template.

        Args:
            template_id: Template to use
            workspace_id: Target workspace
            parent_id: Optional parent page

        Returns:
            dict: Created page data
        """
        template = request.env["ipai.page.template"].browse(template_id)
        if not template.exists():
            return {"error": "Template not found", "code": 404}

        page = template.action_create_page(workspace_id, parent_id)
        return {
            "success": True,
            "page_id": page.id,
            "page_name": page.name,
        }
