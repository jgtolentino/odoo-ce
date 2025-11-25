# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestWorkspace(TransactionCase):
    """Test cases for ipai.workspace model."""

    def setUp(self):
        super().setUp()
        self.Workspace = self.env["ipai.workspace"]
        self.Page = self.env["ipai.page"]
        self.Block = self.env["ipai.block"]
        self.user_admin = self.env.ref("base.user_admin")
        self.user_demo = self.env.ref("base.user_demo")

    def test_create_workspace(self):
        """Test basic workspace creation."""
        workspace = self.Workspace.create(
            {
                "name": "Test Workspace",
                "description": "A test workspace",
                "privacy": "shared",
            }
        )
        self.assertEqual(workspace.name, "Test Workspace")
        self.assertEqual(workspace.privacy, "shared")
        self.assertEqual(workspace.owner_id, self.env.user)
        # Owner should be automatically added to members
        self.assertIn(self.env.user, workspace.member_ids)

    def test_workspace_privacy_private(self):
        """Test private workspace access."""
        workspace = self.Workspace.create(
            {
                "name": "Private Workspace",
                "privacy": "private",
                "owner_id": self.user_admin.id,
            }
        )
        self.assertEqual(workspace.privacy, "private")
        self.assertTrue(workspace._check_access(self.user_admin, "read"))

    def test_workspace_member_management(self):
        """Test adding and removing members."""
        workspace = self.Workspace.create(
            {
                "name": "Member Test Workspace",
                "privacy": "shared",
                "owner_id": self.user_admin.id,
            }
        )
        # Add member
        workspace.action_add_member(self.user_demo.id)
        self.assertIn(self.user_demo, workspace.member_ids)

        # Remove member
        workspace.action_remove_member(self.user_demo.id)
        self.assertNotIn(self.user_demo, workspace.member_ids)

    def test_cannot_remove_owner(self):
        """Test that owner cannot be removed from members."""
        workspace = self.Workspace.sudo(self.user_admin).create(
            {
                "name": "Owner Test Workspace",
                "privacy": "shared",
                "owner_id": self.user_admin.id,
            }
        )
        with self.assertRaises(ValidationError):
            workspace.action_remove_member(self.user_admin.id)


class TestPage(TransactionCase):
    """Test cases for ipai.page model."""

    def setUp(self):
        super().setUp()
        self.Workspace = self.env["ipai.workspace"]
        self.Page = self.env["ipai.page"]
        self.workspace = self.Workspace.create(
            {
                "name": "Test Workspace",
                "privacy": "shared",
            }
        )

    def test_create_page(self):
        """Test basic page creation."""
        page = self.Page.create(
            {
                "name": "Test Page",
                "workspace_id": self.workspace.id,
            }
        )
        self.assertEqual(page.name, "Test Page")
        self.assertEqual(page.workspace_id, self.workspace)
        self.assertEqual(page.depth, 0)

    def test_page_hierarchy(self):
        """Test parent/child page relationships."""
        parent = self.Page.create(
            {
                "name": "Parent Page",
                "workspace_id": self.workspace.id,
            }
        )
        child = self.Page.create(
            {
                "name": "Child Page",
                "workspace_id": self.workspace.id,
                "parent_id": parent.id,
            }
        )
        self.assertEqual(child.parent_id, parent)
        self.assertIn(child, parent.child_ids)
        self.assertEqual(parent.child_count, 1)

    def test_page_breadcrumb(self):
        """Test breadcrumb generation."""
        parent = self.Page.create(
            {
                "name": "Parent",
                "workspace_id": self.workspace.id,
            }
        )
        child = self.Page.create(
            {
                "name": "Child",
                "workspace_id": self.workspace.id,
                "parent_id": parent.id,
            }
        )
        breadcrumb = child.get_breadcrumb()
        self.assertEqual(len(breadcrumb), 2)
        self.assertEqual(breadcrumb[0]["name"], "Parent")
        self.assertEqual(breadcrumb[1]["name"], "Child")

    def test_no_recursive_pages(self):
        """Test that circular references are prevented."""
        page1 = self.Page.create(
            {
                "name": "Page 1",
                "workspace_id": self.workspace.id,
            }
        )
        page2 = self.Page.create(
            {
                "name": "Page 2",
                "workspace_id": self.workspace.id,
                "parent_id": page1.id,
            }
        )
        with self.assertRaises(ValidationError):
            page1.parent_id = page2.id


class TestBlock(TransactionCase):
    """Test cases for ipai.block model."""

    def setUp(self):
        super().setUp()
        self.Workspace = self.env["ipai.workspace"]
        self.Page = self.env["ipai.page"]
        self.Block = self.env["ipai.block"]
        self.workspace = self.Workspace.create(
            {
                "name": "Test Workspace",
                "privacy": "shared",
            }
        )
        self.page = self.Page.create(
            {
                "name": "Test Page",
                "workspace_id": self.workspace.id,
            }
        )

    def test_create_block(self):
        """Test basic block creation."""
        block = self.Block.create(
            {
                "page_id": self.page.id,
                "block_type": "paragraph",
                "content": "Test content",
            }
        )
        self.assertEqual(block.block_type, "paragraph")
        self.assertEqual(block.content, "Test content")
        self.assertEqual(block.page_id, self.page)

    def test_todo_block_toggle(self):
        """Test todo block completion toggle."""
        todo = self.Block.create(
            {
                "page_id": self.page.id,
                "block_type": "todo",
                "content": "Test todo",
                "is_checked": False,
            }
        )
        self.assertFalse(todo.is_checked)
        todo.action_toggle_todo()
        self.assertTrue(todo.is_checked)
        todo.action_toggle_todo()
        self.assertFalse(todo.is_checked)

    def test_block_to_json(self):
        """Test block JSON serialization."""
        block = self.Block.create(
            {
                "page_id": self.page.id,
                "block_type": "callout",
                "content": "Important note",
                "callout_icon": "⚠️",
                "callout_color": "yellow",
            }
        )
        json_data = block.to_json()
        self.assertEqual(json_data["type"], "callout")
        self.assertEqual(json_data["content"], "Important note")
        self.assertEqual(json_data["callout_icon"], "⚠️")
        self.assertEqual(json_data["callout_color"], "yellow")


class TestBacklink(TransactionCase):
    """Test cases for ipai.backlink model."""

    def setUp(self):
        super().setUp()
        self.Workspace = self.env["ipai.workspace"]
        self.Page = self.env["ipai.page"]
        self.Backlink = self.env["ipai.backlink"]
        self.workspace = self.Workspace.create(
            {
                "name": "Test Workspace",
                "privacy": "shared",
            }
        )

    def test_create_backlink(self):
        """Test backlink creation."""
        page1 = self.Page.create(
            {
                "name": "Source Page",
                "workspace_id": self.workspace.id,
            }
        )
        page2 = self.Page.create(
            {
                "name": "Target Page",
                "workspace_id": self.workspace.id,
            }
        )
        backlink = self.Backlink.create(
            {
                "source_page_id": page1.id,
                "target_page_id": page2.id,
                "link_text": "Target Page",
            }
        )
        self.assertEqual(backlink.source_page_id, page1)
        self.assertEqual(backlink.target_page_id, page2)
        self.assertIn(backlink, page2.backlink_ids)

    def test_backlink_graph(self):
        """Test page relationship graph generation."""
        page1 = self.Page.create(
            {
                "name": "Page 1",
                "workspace_id": self.workspace.id,
            }
        )
        page2 = self.Page.create(
            {
                "name": "Page 2",
                "workspace_id": self.workspace.id,
            }
        )
        self.Backlink.create(
            {
                "source_page_id": page1.id,
                "target_page_id": page2.id,
                "link_text": "Page 2",
            }
        )
        graph = self.Backlink.get_page_graph(self.workspace.id)
        self.assertEqual(len(graph["nodes"]), 2)
        self.assertEqual(len(graph["edges"]), 1)


class TestTemplate(TransactionCase):
    """Test cases for ipai.page.template model."""

    def setUp(self):
        super().setUp()
        self.Workspace = self.env["ipai.workspace"]
        self.Template = self.env["ipai.page.template"]
        self.workspace = self.Workspace.create(
            {
                "name": "Test Workspace",
                "privacy": "shared",
            }
        )

    def test_create_from_template(self):
        """Test page creation from template."""
        template = self.Template.create(
            {
                "name": "Test Template",
                "default_title": "New Doc",
                "icon": "📋",
                "is_global": True,
                "content_html": "<h1>Template Content</h1>",
            }
        )
        page = template.action_create_page(self.workspace.id)
        self.assertEqual(page.name, "New Doc")
        self.assertEqual(page.icon, "📋")
        self.assertEqual(page.template_id, template)
        self.assertIn("Template Content", page.content_html)
