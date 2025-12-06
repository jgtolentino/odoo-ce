# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Security Control Tests
======================

Unit tests for security.control model.
"""
from odoo.tests.common import TransactionCase


class TestSecurityControl(TransactionCase):
    """Test cases for security.control model."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Control = cls.env["security.control"]
        cls.Framework = cls.env["security.framework"]

        # Create test framework
        cls.framework = cls.Framework.create({
            "name": "Test Framework",
            "code": "TEST",
            "category": "info_security",
        })

    def test_create_control(self):
        """Test basic control creation."""
        control = self.Control.create({
            "code": "TEST-001",
            "name": "Test Control",
            "description": "Test description",
            "framework_id": self.framework.id,
        })
        self.assertEqual(control.code, "TEST-001")
        self.assertEqual(control.status, "not_implemented")

    def test_mark_implemented_action(self):
        """Test marking control as implemented."""
        control = self.Control.create({
            "code": "TEST-002",
            "name": "Implement Test Control",
            "description": "Test",
            "framework_id": self.framework.id,
        })
        control.action_mark_implemented()
        self.assertEqual(control.status, "implemented")
        self.assertTrue(control.implementation_date)

    def test_mark_tested_action(self):
        """Test marking control as tested."""
        control = self.Control.create({
            "code": "TEST-003",
            "name": "Test Test Control",
            "description": "Test",
            "framework_id": self.framework.id,
            "status": "implemented",
        })
        control.action_mark_tested()
        self.assertEqual(control.status, "tested")
        self.assertEqual(control.test_result, "passed")
        self.assertTrue(control.last_test_date)

    def test_control_color(self):
        """Test color computation based on status."""
        control = self.Control.create({
            "code": "TEST-004",
            "name": "Color Test Control",
            "description": "Test",
            "framework_id": self.framework.id,
        })
        # Not implemented = red (1)
        self.assertEqual(control.color, 1)

        control.status = "implemented"
        self.assertEqual(control.color, 10)  # Green

        control.status = "tested"
        self.assertEqual(control.color, 11)  # Light green

    def test_framework_coverage_update(self):
        """Test that framework coverage updates when controls are implemented."""
        control1 = self.Control.create({
            "code": "COV-001",
            "name": "Coverage Control 1",
            "description": "Test",
            "framework_id": self.framework.id,
            "status": "not_implemented",
        })
        control2 = self.Control.create({
            "code": "COV-002",
            "name": "Coverage Control 2",
            "description": "Test",
            "framework_id": self.framework.id,
            "status": "implemented",
        })

        # Refresh framework
        self.framework.invalidate_recordset()

        # 1 implemented out of 2 = 50%
        self.assertEqual(self.framework.coverage_percentage, 50.0)
