# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)
"""
Tests for the project.brief model.

Covers:
- Basic CRUD operations
- Constraint validation (deadline, budget)
- Status workflow transitions
- Lock/unlock behavior
- Access control
"""

from datetime import date, timedelta

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestProjectBrief(TransactionCase):
    """Test cases for project.brief model."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()

        # Create test project
        cls.project = cls.env["project.project"].create({
            "name": "Test Project",
        })

        # Create test client (partner)
        cls.client = cls.env["res.partner"].create({
            "name": "Test Client Company",
            "is_company": True,
        })

        # Create test user (non-admin)
        cls.test_user = cls.env["res.users"].create({
            "name": "Test User",
            "login": "test_project_brief_user",
            "email": "test@example.com",
            "groups_id": [
                (4, cls.env.ref("project.group_project_user").id),
            ],
        })

        cls.ProjectBrief = cls.env["project.brief"]

    def _create_brief(self, **kwargs):
        """Helper to create a brief with default values."""
        vals = {
            "name": "Test Brief",
            "project_id": self.project.id,
            "client_id": self.client.id,
        }
        vals.update(kwargs)
        return self.ProjectBrief.create(vals)

    # -------------------------------------------------------------------------
    # Basic CRUD Tests
    # -------------------------------------------------------------------------
    def test_create_brief_basic(self):
        """Test creating a basic brief."""
        brief = self._create_brief()

        self.assertEqual(brief.status, "draft")
        self.assertEqual(brief.project_id, self.project)
        self.assertEqual(brief.client_id, self.client)
        self.assertFalse(brief.is_locked)

    def test_create_brief_with_all_fields(self):
        """Test creating a brief with all fields populated."""
        deadline = date.today() + timedelta(days=30)
        brief = self._create_brief(
            brand_name="Test Brand",
            objective="Test objective",
            target_audience="Test audience",
            key_message="Test message",
            deliverables="Test deliverables",
            budget=100000.0,
            deadline=deadline,
        )

        self.assertEqual(brief.brand_name, "Test Brand")
        self.assertEqual(brief.objective, "Test objective")
        self.assertEqual(brief.budget, 100000.0)
        self.assertEqual(brief.deadline, deadline)

    def test_read_brief(self):
        """Test reading brief fields."""
        brief = self._create_brief(brand_name="Read Test")
        read_data = brief.read(["name", "brand_name", "status"])[0]

        self.assertEqual(read_data["name"], "Test Brief")
        self.assertEqual(read_data["brand_name"], "Read Test")
        self.assertEqual(read_data["status"], "draft")

    def test_update_brief(self):
        """Test updating brief fields."""
        brief = self._create_brief()
        brief.write({"brand_name": "Updated Brand"})

        self.assertEqual(brief.brand_name, "Updated Brand")

    def test_delete_draft_brief(self):
        """Test deleting a draft brief."""
        brief = self._create_brief()
        brief_id = brief.id
        brief.unlink()

        self.assertFalse(self.ProjectBrief.browse(brief_id).exists())

    # -------------------------------------------------------------------------
    # Constraint Tests
    # -------------------------------------------------------------------------
    def test_deadline_cannot_be_past(self):
        """Test that deadline cannot be in the past."""
        with self.assertRaises(ValidationError):
            self._create_brief(deadline=date.today() - timedelta(days=1))

    def test_deadline_can_be_today(self):
        """Test that deadline can be today."""
        brief = self._create_brief(deadline=date.today())
        self.assertEqual(brief.deadline, date.today())

    def test_deadline_can_be_future(self):
        """Test that deadline can be in the future."""
        future_date = date.today() + timedelta(days=30)
        brief = self._create_brief(deadline=future_date)
        self.assertEqual(brief.deadline, future_date)

    def test_budget_cannot_be_negative(self):
        """Test that budget cannot be negative."""
        with self.assertRaises(ValidationError):
            self._create_brief(budget=-1000)

    def test_budget_can_be_zero(self):
        """Test that budget can be zero."""
        brief = self._create_brief(budget=0)
        self.assertEqual(brief.budget, 0)

    # -------------------------------------------------------------------------
    # Status Workflow Tests
    # -------------------------------------------------------------------------
    def test_status_draft_to_in_review(self):
        """Test transitioning from draft to in_review."""
        brief = self._create_brief()
        brief.action_mark_in_review()

        self.assertEqual(brief.status, "in_review")

    def test_status_in_review_to_approved(self):
        """Test transitioning from in_review to approved."""
        brief = self._create_brief()
        brief.action_mark_in_review()
        brief.action_approve()

        self.assertEqual(brief.status, "approved")
        self.assertTrue(brief.is_locked)

    def test_status_to_on_hold(self):
        """Test putting a brief on hold."""
        brief = self._create_brief()
        brief.action_mark_in_review()
        brief.action_hold()

        self.assertEqual(brief.status, "on_hold")

    def test_status_to_cancelled(self):
        """Test cancelling a brief."""
        brief = self._create_brief()
        brief.action_cancel()

        self.assertEqual(brief.status, "cancelled")

    def test_status_reset_to_draft(self):
        """Test resetting a cancelled brief to draft."""
        brief = self._create_brief()
        brief.action_cancel()
        brief.action_reset_to_draft()

        self.assertEqual(brief.status, "draft")
        self.assertFalse(brief.is_locked)

    def test_cannot_approve_draft(self):
        """Test that draft briefs cannot be directly approved."""
        brief = self._create_brief()

        with self.assertRaises(ValidationError):
            brief.action_approve()

    def test_cannot_cancel_approved(self):
        """Test that approved briefs cannot be cancelled."""
        brief = self._create_brief()
        brief.action_mark_in_review()
        brief.action_approve()

        with self.assertRaises(ValidationError):
            brief.action_cancel()

    def test_cannot_delete_approved(self):
        """Test that approved briefs cannot be deleted."""
        brief = self._create_brief()
        brief.action_mark_in_review()
        brief.action_approve()

        with self.assertRaises(ValidationError):
            brief.unlink()

    # -------------------------------------------------------------------------
    # Lock/Unlock Tests
    # -------------------------------------------------------------------------
    def test_approved_brief_is_locked(self):
        """Test that approved briefs are automatically locked."""
        brief = self._create_brief()
        brief.action_mark_in_review()
        brief.action_approve()

        self.assertTrue(brief.is_locked)

    def test_locked_brief_cannot_be_edited_by_user(self):
        """Test that locked briefs cannot be edited by non-admin users."""
        brief = self._create_brief()
        brief.action_mark_in_review()
        brief.action_approve()

        with self.assertRaises(ValidationError):
            brief.with_user(self.test_user).write({"brand_name": "Changed"})

    def test_admin_can_unlock_brief(self):
        """Test that admins can unlock briefs."""
        brief = self._create_brief()
        brief.action_mark_in_review()
        brief.action_approve()

        # Admin should be able to unlock
        admin_user = self.env.ref("base.user_admin")
        brief.with_user(admin_user).action_unlock()

        self.assertFalse(brief.is_locked)

    def test_non_admin_cannot_unlock_brief(self):
        """Test that non-admin users cannot unlock briefs."""
        brief = self._create_brief()
        brief.action_mark_in_review()
        brief.action_approve()

        with self.assertRaises(ValidationError):
            brief.with_user(self.test_user).action_unlock()

    # -------------------------------------------------------------------------
    # Computed Fields Tests
    # -------------------------------------------------------------------------
    def test_days_until_deadline_future(self):
        """Test days_until_deadline computation for future date."""
        future_date = date.today() + timedelta(days=10)
        brief = self._create_brief(deadline=future_date)

        self.assertEqual(brief.days_until_deadline, 10)

    def test_days_until_deadline_no_deadline(self):
        """Test days_until_deadline when no deadline is set."""
        brief = self._create_brief()

        self.assertEqual(brief.days_until_deadline, 0)

    # -------------------------------------------------------------------------
    # Edge Cases
    # -------------------------------------------------------------------------
    def test_on_hold_to_in_review(self):
        """Test transitioning from on_hold back to in_review."""
        brief = self._create_brief()
        brief.action_hold()
        brief.action_mark_in_review()

        self.assertEqual(brief.status, "in_review")

    def test_on_hold_to_approved(self):
        """Test transitioning from on_hold to approved."""
        brief = self._create_brief()
        brief.action_mark_in_review()
        brief.action_hold()
        brief.action_approve()

        self.assertEqual(brief.status, "approved")
        self.assertTrue(brief.is_locked)

    def test_cancelled_cannot_be_held(self):
        """Test that cancelled briefs cannot be put on hold."""
        brief = self._create_brief()
        brief.action_cancel()

        with self.assertRaises(ValidationError):
            brief.action_hold()
