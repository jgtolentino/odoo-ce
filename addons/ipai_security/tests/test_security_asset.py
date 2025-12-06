# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Security Asset Tests
====================

Unit tests for security.asset model.
"""
from odoo.tests.common import TransactionCase


class TestSecurityAsset(TransactionCase):
    """Test cases for security.asset model."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.Asset = cls.env["security.asset"]
        cls.DataCategory = cls.env["security.data.category"]

        # Create test data categories
        cls.cat_personal = cls.DataCategory.create({
            "name": "Test Personal Info",
            "code": "TEST-PI",
            "dpa_classification": "personal",
            "sensitivity_level": "confidential",
        })
        cls.cat_sensitive = cls.DataCategory.create({
            "name": "Test Sensitive Info",
            "code": "TEST-SPI",
            "dpa_classification": "sensitive_personal",
            "sensitivity_level": "restricted",
        })
        cls.cat_non_personal = cls.DataCategory.create({
            "name": "Test Non-Personal",
            "code": "TEST-NPD",
            "dpa_classification": "non_personal",
            "sensitivity_level": "public",
        })

    def test_create_asset(self):
        """Test basic asset creation."""
        asset = self.Asset.create({
            "name": "Test Asset",
            "asset_type": "application",
            "environment": "production",
        })
        self.assertEqual(asset.name, "Test Asset")
        self.assertEqual(asset.asset_type, "application")
        self.assertEqual(asset.status, "active")

    def test_handles_pii_computation(self):
        """Test that handles_pii is computed correctly."""
        # Asset without PII
        asset_no_pii = self.Asset.create({
            "name": "No PII Asset",
            "asset_type": "application",
            "data_category_ids": [(6, 0, [self.cat_non_personal.id])],
        })
        self.assertFalse(asset_no_pii.handles_pii)

        # Asset with PII
        asset_with_pii = self.Asset.create({
            "name": "PII Asset",
            "asset_type": "application",
            "data_category_ids": [(6, 0, [self.cat_personal.id])],
        })
        self.assertTrue(asset_with_pii.handles_pii)

    def test_handles_sensitive_computation(self):
        """Test that handles_sensitive is computed correctly."""
        # Asset without sensitive data
        asset_no_sensitive = self.Asset.create({
            "name": "No Sensitive Asset",
            "asset_type": "application",
            "data_category_ids": [(6, 0, [self.cat_personal.id])],
        })
        self.assertFalse(asset_no_sensitive.handles_sensitive)

        # Asset with sensitive data
        asset_with_sensitive = self.Asset.create({
            "name": "Sensitive Asset",
            "asset_type": "application",
            "data_category_ids": [(6, 0, [self.cat_sensitive.id])],
        })
        self.assertTrue(asset_with_sensitive.handles_sensitive)

    def test_risk_score_computation(self):
        """Test risk score calculation."""
        asset = self.Asset.create({
            "name": "Risk Test Asset",
            "asset_type": "application",
            "risk_level": "low",
        })
        self.assertEqual(asset.risk_score, 20)

        asset.risk_level = "critical"
        self.assertEqual(asset.risk_score, 90)

        # With sensitive data
        asset.data_category_ids = [(6, 0, [self.cat_sensitive.id])]
        self.assertEqual(asset.risk_score, 100)  # 90 + 10 for sensitive, capped at 100

    def test_asset_type_values(self):
        """Test that all asset types are valid."""
        valid_types = [
            "application", "agent", "droplet", "database",
            "bucket", "api", "network", "other"
        ]
        for asset_type in valid_types:
            asset = self.Asset.create({
                "name": f"Test {asset_type}",
                "asset_type": asset_type,
            })
            self.assertEqual(asset.asset_type, asset_type)
