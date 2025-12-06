# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Security Risk Tests
===================

Unit tests for security.risk model.
"""
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestSecurityRisk(TransactionCase):
    """Test cases for security.risk model."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Risk = cls.env["security.risk"]
        cls.Control = cls.env["security.control"]
        cls.Framework = cls.env["security.framework"]

        # Create test framework
        cls.framework = cls.Framework.create({
            "name": "Test Framework",
            "code": "TEST",
            "category": "info_security",
        })

    def test_create_risk(self):
        """Test basic risk creation."""
        risk = self.Risk.create({
            "name": "Test Risk",
            "description": "Test description",
            "severity": "3_moderate",
            "likelihood": "3_possible",
        })
        self.assertEqual(risk.name, "Test Risk")
        self.assertEqual(risk.status, "open")
        self.assertTrue(risk.reference.startswith("RISK-"))

    def test_risk_score_computation(self):
        """Test inherent and residual risk score calculation."""
        risk = self.Risk.create({
            "name": "Score Test Risk",
            "description": "Test",
            "severity": "3_moderate",
            "likelihood": "3_possible",
        })
        # 3 x 3 = 9
        self.assertEqual(risk.inherent_risk_score, 9)
        # No controls, so residual = inherent
        self.assertEqual(risk.residual_risk_score, 9)

        # Critical severity, almost certain likelihood
        risk.severity = "5_critical"
        risk.likelihood = "5_almost_certain"
        # 5 x 5 = 25
        self.assertEqual(risk.inherent_risk_score, 25)

    def test_risk_level_computation(self):
        """Test risk level determination from score."""
        # Low risk (score < 6)
        risk_low = self.Risk.create({
            "name": "Low Risk",
            "description": "Test",
            "severity": "1_negligible",
            "likelihood": "1_rare",
        })
        self.assertEqual(risk_low.risk_level, "low")

        # Critical risk (score >= 20)
        risk_critical = self.Risk.create({
            "name": "Critical Risk",
            "description": "Test",
            "severity": "5_critical",
            "likelihood": "5_almost_certain",
        })
        self.assertEqual(risk_critical.risk_level, "critical")

    def test_control_effectiveness(self):
        """Test control effectiveness calculation."""
        # Create controls
        control1 = self.Control.create({
            "code": "TEST-1",
            "name": "Test Control 1",
            "description": "Test",
            "framework_id": self.framework.id,
            "status": "implemented",
        })
        control2 = self.Control.create({
            "code": "TEST-2",
            "name": "Test Control 2",
            "description": "Test",
            "framework_id": self.framework.id,
            "status": "not_implemented",
        })

        risk = self.Risk.create({
            "name": "Control Test Risk",
            "description": "Test",
            "control_ids": [(6, 0, [control1.id, control2.id])],
        })

        # 1 implemented out of 2 = 50%
        self.assertEqual(risk.control_effectiveness, 50.0)

    def test_resolution_date_constraint(self):
        """Test that target resolution cannot be before identification."""
        with self.assertRaises(ValidationError):
            self.Risk.create({
                "name": "Invalid Date Risk",
                "description": "Test",
                "identified_date": "2024-06-01",
                "target_resolution_date": "2024-01-01",
            })

    def test_close_risk_action(self):
        """Test closing a risk."""
        risk = self.Risk.create({
            "name": "Close Test Risk",
            "description": "Test",
        })
        self.assertEqual(risk.status, "open")

        risk.action_close_risk()
        self.assertEqual(risk.status, "closed")
        self.assertTrue(risk.actual_resolution_date)

    def test_accept_risk_action(self):
        """Test accepting a risk."""
        risk = self.Risk.create({
            "name": "Accept Test Risk",
            "description": "Test",
        })
        risk.action_accept_risk()
        self.assertEqual(risk.status, "accepted")
