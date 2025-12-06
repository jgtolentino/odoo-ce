# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
AI System Tests
===============

Unit tests for ai.system model.
"""
from odoo.tests.common import TransactionCase


class TestAISystem(TransactionCase):
    """Test cases for ai.system model."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.AISystem = cls.env["ai.system"]
        cls.DataCategory = cls.env["security.data.category"]

        # Create test data categories
        cls.cat_personal = cls.DataCategory.create({
            "name": "Test Personal Info",
            "code": "AI-TEST-PI",
            "dpa_classification": "personal",
            "sensitivity_level": "confidential",
        })

    def test_create_ai_system(self):
        """Test basic AI system creation."""
        system = self.AISystem.create({
            "name": "Test AI System",
            "system_type": "agent",
            "provider": "anthropic",
            "models_used": "claude-3.5-sonnet",
            "intended_use": "Testing",
        })
        self.assertEqual(system.name, "Test AI System")
        self.assertEqual(system.eval_status, "not_evaluated")
        self.assertEqual(system.status, "development")

    def test_handles_pii_computation(self):
        """Test PII handling detection."""
        system = self.AISystem.create({
            "name": "PII Test System",
            "system_type": "agent",
            "intended_use": "Testing",
            "data_category_ids": [(6, 0, [self.cat_personal.id])],
        })
        self.assertTrue(system.handles_pii)

    def test_evaluation_workflow(self):
        """Test evaluation status transitions."""
        system = self.AISystem.create({
            "name": "Eval Test System",
            "system_type": "agent",
            "intended_use": "Testing",
        })
        self.assertEqual(system.eval_status, "not_evaluated")

        system.action_start_evaluation()
        self.assertEqual(system.eval_status, "in_progress")

        system.action_complete_evaluation()
        self.assertEqual(system.eval_status, "completed")
        self.assertTrue(system.last_eval_date)

    def test_risk_color_computation(self):
        """Test color computation based on risk level."""
        system = self.AISystem.create({
            "name": "Color Test System",
            "system_type": "agent",
            "intended_use": "Testing",
            "risk_level": "minimal",
        })
        self.assertEqual(system.color, 10)  # Green for low risk

        system.risk_level = "high"
        self.assertEqual(system.color, 1)  # Red for high risk

    def test_ai_provider_values(self):
        """Test all valid AI provider values."""
        valid_providers = [
            "anthropic", "openai", "google", "huggingface",
            "local", "custom", "multiple", "other"
        ]
        for provider in valid_providers:
            system = self.AISystem.create({
                "name": f"Test {provider}",
                "system_type": "agent",
                "provider": provider,
                "intended_use": "Testing",
            })
            self.assertEqual(system.provider, provider)
