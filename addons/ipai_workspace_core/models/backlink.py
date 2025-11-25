# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class IpaiBacklink(models.Model):
    """
    Backlink - Tracks bi-directional page references.

    When page A references page B with [[Page B]],
    this creates a backlink record that allows:
    - Page B to see all pages referencing it
    - Navigation between related pages
    - Graph visualization of page relationships
    """
    _name = "ipai.backlink"
    _description = "IPAI Page Backlink"
    _order = "create_date desc"

    # -------------------------------------------------------------------------
    # FIELDS
    # -------------------------------------------------------------------------
    source_page_id = fields.Many2one(
        "ipai.page",
        string="Source Page",
        required=True,
        ondelete="cascade",
        index=True,
        help="The page containing the link",
    )
    target_page_id = fields.Many2one(
        "ipai.page",
        string="Target Page",
        required=True,
        ondelete="cascade",
        index=True,
        help="The page being referenced",
    )

    # Link metadata
    link_text = fields.Char(
        string="Link Text",
        help="The text used in the [[link]]",
    )
    link_type = fields.Selection([
        ("mention", "Mention [[Page]]"),
        ("embed", "Embed /embed"),
        ("reference", "Reference"),
    ], string="Link Type", default="mention")

    # Context
    workspace_id = fields.Many2one(
        related="source_page_id.workspace_id",
        string="Workspace",
        store=True,
        index=True,
    )

    # Computed
    source_page_name = fields.Char(
        related="source_page_id.name",
        string="Source Name",
    )
    target_page_name = fields.Char(
        related="target_page_id.name",
        string="Target Name",
    )

    # -------------------------------------------------------------------------
    # CONSTRAINTS
    # -------------------------------------------------------------------------
    _sql_constraints = [
        (
            "unique_backlink",
            "unique(source_page_id, target_page_id, link_type)",
            "Duplicate backlink already exists!",
        ),
        (
            "no_self_reference",
            "check(source_page_id != target_page_id)",
            "A page cannot link to itself!",
        ),
    ]

    # -------------------------------------------------------------------------
    # METHODS
    # -------------------------------------------------------------------------
    @api.model
    def get_backlinks_for_page(self, page_id):
        """
        Get all backlinks for a page (pages that reference it).

        :param page_id: int - Target page ID
        :return: list of dicts with source page info
        """
        backlinks = self.search([("target_page_id", "=", page_id)])
        return [{
            "id": bl.source_page_id.id,
            "name": bl.source_page_id.name,
            "icon": bl.source_page_id.icon,
            "link_text": bl.link_text,
            "link_type": bl.link_type,
        } for bl in backlinks]

    @api.model
    def get_outgoing_links(self, page_id):
        """
        Get all outgoing links from a page.

        :param page_id: int - Source page ID
        :return: list of dicts with target page info
        """
        links = self.search([("source_page_id", "=", page_id)])
        return [{
            "id": link.target_page_id.id,
            "name": link.target_page_id.name,
            "icon": link.target_page_id.icon,
            "link_text": link.link_text,
            "link_type": link.link_type,
        } for link in links]

    @api.model
    def get_page_graph(self, workspace_id, max_depth=2):
        """
        Build a graph of page relationships for visualization.

        :param workspace_id: int - Workspace to analyze
        :param max_depth: int - Maximum traversal depth
        :return: dict with nodes and edges for graph visualization
        """
        pages = self.env["ipai.page"].search([
            ("workspace_id", "=", workspace_id),
        ])
        backlinks = self.search([
            ("workspace_id", "=", workspace_id),
        ])

        nodes = [{
            "id": page.id,
            "label": page.name,
            "icon": page.icon,
        } for page in pages]

        edges = [{
            "source": bl.source_page_id.id,
            "target": bl.target_page_id.id,
            "label": bl.link_text,
        } for bl in backlinks]

        return {
            "nodes": nodes,
            "edges": edges,
        }
