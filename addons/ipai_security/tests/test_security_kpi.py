# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Security KPI Tests
==================

Unit tests for security.kpi model.
"""
from odoo.tests.common import TransactionCase


class TestSecurityKPI(TransactionCase):
    """Test cases for security.kpi model."""

    @classmethod
    def setUpClass(cls):
        """Set up test data."""
        super().setUpClass()
        cls.KPI = cls.env["security.kpi"]
        cls.Risk = cls.env["security.risk"]
        cls.Asset = cls.env["security.asset"]
        cls.Framework = cls.env["security.framework"]

        # Create test framework
        cls.framework = cls.Framework.create({
            "name": "KPI Test Framework",
            "code": "KPITEST",
            "category": "info_security",
        })

    def test_capture_snapshot(self):
        """Test KPI snapshot capture."""
        # Create some test data
        self.Asset.create({
            "name": "KPI Test Asset",
            "asset_type": "application",
            "in_scope": True,
        })
        self.Risk.create({
            "name": "KPI Test Risk",
            "description": "Test",
            "status": "open",
        })

        # Capture snapshot
        snapshot = self.KPI.capture_snapshot()

        self.assertTrue(snapshot.id)
        self.assertTrue(snapshot.snapshot_date)
        self.assertGreaterEqual(snapshot.total_assets, 1)
        self.assertGreaterEqual(snapshot.open_risks, 1)
        self.assertGreaterEqual(snapshot.health_score, 0)
        self.assertLessEqual(snapshot.health_score, 100)

    def test_get_current_kpis(self):
        """Test getting current KPIs without snapshot."""
        kpis = self.KPI.get_current_kpis()

        self.assertIn("risks_open", kpis)
        self.assertIn("health_score", kpis)
        self.assertIn("framework_coverage", kpis)
        self.assertIn("timestamp", kpis)

    def test_health_score_calculation(self):
        """Test health score calculation logic."""
        # Create critical risk to lower health score
        for i in range(3):
            self.Risk.create({
                "name": f"Critical Risk {i}",
                "description": "Test",
                "severity": "5_critical",
                "likelihood": "5_almost_certain",
                "status": "open",
            })

        kpis = self.KPI.get_current_kpis()

        # With 3 critical risks, score should be reduced
        self.assertLess(kpis["health_score"], 100)

    def test_snapshot_name_generation(self):
        """Test automatic name generation for snapshots."""
        snapshot = self.KPI.capture_snapshot()
        self.assertTrue(snapshot.name.startswith("Security KPI -"))
