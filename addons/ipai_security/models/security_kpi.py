# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Security KPI Model
==================

Key Performance Indicators for the Security & Compliance Workbench.
Provides computed metrics for the security dashboard including:
- Open risk counts
- Incident statistics
- Framework coverage percentages
- Control implementation status
- AI system governance metrics
"""
from datetime import timedelta

from odoo import api, fields, models


class SecurityKPI(models.Model):
    """
    Security KPI snapshot record.

    This model captures point-in-time KPI snapshots for historical
    tracking and trend analysis.

    Attributes:
        _name: Model technical name
        _description: Human-readable model description
        _order: Default ordering (most recent first)
    """

    _name = "security.kpi"
    _description = "Security KPI Snapshot"
    _order = "snapshot_date DESC, id DESC"

    name = fields.Char(
        string="Snapshot Name",
        compute="_compute_name",
        store=True,
    )
    snapshot_date = fields.Datetime(
        string="Snapshot Date",
        default=fields.Datetime.now,
        required=True,
    )
    # Risk metrics
    total_risks = fields.Integer(
        string="Total Risks",
    )
    open_risks = fields.Integer(
        string="Open Risks",
    )
    critical_risks = fields.Integer(
        string="Critical Risks",
    )
    high_risks = fields.Integer(
        string="High Risks",
    )
    mitigated_risks = fields.Integer(
        string="Mitigated Risks",
    )
    # Incident metrics
    total_incidents = fields.Integer(
        string="Total Incidents",
    )
    incidents_30d = fields.Integer(
        string="Incidents (30 Days)",
    )
    open_incidents = fields.Integer(
        string="Open Incidents",
    )
    critical_incidents = fields.Integer(
        string="Critical Incidents",
    )
    # Asset metrics
    total_assets = fields.Integer(
        string="Total Assets",
    )
    assets_in_scope = fields.Integer(
        string="Assets in Scope",
    )
    assets_with_pii = fields.Integer(
        string="Assets with PII",
    )
    # Control metrics
    total_controls = fields.Integer(
        string="Total Controls",
    )
    implemented_controls = fields.Integer(
        string="Implemented Controls",
    )
    tested_controls = fields.Integer(
        string="Tested Controls",
    )
    # Framework coverage
    dpa_coverage = fields.Float(
        string="DPA Coverage %",
    )
    iso_27001_coverage = fields.Float(
        string="ISO 27001 Coverage %",
    )
    soc2_coverage = fields.Float(
        string="SOC 2 Coverage %",
    )
    ai_gov_coverage = fields.Float(
        string="AI Governance Coverage %",
    )
    # AI system metrics
    total_ai_systems = fields.Integer(
        string="Total AI Systems",
    )
    evaluated_ai_systems = fields.Integer(
        string="Evaluated AI Systems",
    )
    high_risk_ai_systems = fields.Integer(
        string="High Risk AI Systems",
    )
    # Data flow metrics
    total_data_flows = fields.Integer(
        string="Total Data Flows",
    )
    compliant_data_flows = fields.Integer(
        string="Compliant Data Flows",
    )
    data_flows_with_gaps = fields.Integer(
        string="Data Flows with Gaps",
    )
    # Audit metrics
    completed_audits = fields.Integer(
        string="Completed Audits",
    )
    pending_findings = fields.Integer(
        string="Pending Audit Findings",
    )
    # Overall scores
    health_score = fields.Float(
        string="Overall Health Score",
        help="Composite security health score (0-100)",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    @api.depends("snapshot_date")
    def _compute_name(self):
        """Generate name from snapshot date."""
        for kpi in self:
            if kpi.snapshot_date:
                kpi.name = f"Security KPI - {kpi.snapshot_date.strftime('%Y-%m-%d %H:%M')}"
            else:
                kpi.name = "Security KPI"

    @api.model
    def capture_snapshot(self):
        """
        Capture a new KPI snapshot.

        This method calculates all current metrics and creates a new
        KPI record. Can be called via cron job for regular tracking.
        """
        Risk = self.env["security.risk"]
        Incident = self.env["security.incident"]
        Asset = self.env["security.asset"]
        Control = self.env["security.control"]
        Framework = self.env["security.framework"]
        AISystem = self.env["ai.system"]
        DataFlow = self.env["security.data.flow"]
        Audit = self.env["security.audit"]
        Finding = self.env["security.audit.finding"]

        # Risk metrics
        all_risks = Risk.search([])
        open_risks = Risk.search([("status", "in", ("open", "in_progress"))])
        critical_risks = Risk.search(
            [("risk_level", "=", "critical"), ("status", "in", ("open", "in_progress"))]
        )
        high_risks = Risk.search(
            [("risk_level", "=", "high"), ("status", "in", ("open", "in_progress"))]
        )
        mitigated_risks = Risk.search([("status", "=", "mitigated")])

        # Incident metrics (last 30 days)
        thirty_days_ago = fields.Datetime.now() - timedelta(days=30)
        all_incidents = Incident.search([])
        incidents_30d = Incident.search([("detected_date", ">=", thirty_days_ago)])
        open_incidents = Incident.search(
            [("status", "not in", ("closed",))]
        )
        critical_incidents = Incident.search(
            [("severity", "=", "4_critical"), ("status", "!=", "closed")]
        )

        # Asset metrics
        all_assets = Asset.search([])
        in_scope_assets = Asset.search([("in_scope", "=", True)])
        pii_assets = Asset.search([("handles_pii", "=", True)])

        # Control metrics
        all_controls = Control.search([])
        implemented_controls = Control.search(
            [("status", "in", ("implemented", "tested"))]
        )
        tested_controls = Control.search([("status", "=", "tested")])

        # Framework coverage
        dpa_coverage = 0.0
        iso_coverage = 0.0
        soc2_coverage = 0.0
        ai_coverage = 0.0

        dpa_framework = Framework.search([("code", "=", "DPA")], limit=1)
        if dpa_framework:
            dpa_coverage = dpa_framework.coverage_percentage

        iso_framework = Framework.search([("code", "=", "ISO27001")], limit=1)
        if iso_framework:
            iso_coverage = iso_framework.coverage_percentage

        soc2_framework = Framework.search([("code", "=", "SOC2")], limit=1)
        if soc2_framework:
            soc2_coverage = soc2_framework.coverage_percentage

        ai_framework = Framework.search([("code", "in", ("AIRM", "ISO42001"))], limit=1)
        if ai_framework:
            ai_coverage = ai_framework.coverage_percentage

        # AI system metrics
        all_ai_systems = AISystem.search([])
        evaluated_ai = AISystem.search([("eval_status", "=", "completed")])
        high_risk_ai = AISystem.search(
            [("risk_level", "in", ("high", "unacceptable"))]
        )

        # Data flow metrics
        all_flows = DataFlow.search([])
        compliant_flows = DataFlow.search([("status", "=", "active")])
        gap_flows = DataFlow.search([("compliance_gap", "=", True)])

        # Audit metrics
        completed_audits = Audit.search([("status", "=", "completed")])
        pending_findings = Finding.search([("status", "in", ("open", "in_progress"))])

        # Calculate health score (0-100)
        health_score = self._calculate_health_score(
            open_risks=len(open_risks),
            critical_risks=len(critical_risks),
            open_incidents=len(open_incidents),
            control_implementation_rate=(
                len(implemented_controls) / len(all_controls) * 100
                if all_controls
                else 0
            ),
            data_flow_compliance_rate=(
                len(compliant_flows) / len(all_flows) * 100 if all_flows else 0
            ),
            ai_evaluation_rate=(
                len(evaluated_ai) / len(all_ai_systems) * 100 if all_ai_systems else 0
            ),
        )

        # Create snapshot
        return self.create({
            "snapshot_date": fields.Datetime.now(),
            "total_risks": len(all_risks),
            "open_risks": len(open_risks),
            "critical_risks": len(critical_risks),
            "high_risks": len(high_risks),
            "mitigated_risks": len(mitigated_risks),
            "total_incidents": len(all_incidents),
            "incidents_30d": len(incidents_30d),
            "open_incidents": len(open_incidents),
            "critical_incidents": len(critical_incidents),
            "total_assets": len(all_assets),
            "assets_in_scope": len(in_scope_assets),
            "assets_with_pii": len(pii_assets),
            "total_controls": len(all_controls),
            "implemented_controls": len(implemented_controls),
            "tested_controls": len(tested_controls),
            "dpa_coverage": dpa_coverage,
            "iso_27001_coverage": iso_coverage,
            "soc2_coverage": soc2_coverage,
            "ai_gov_coverage": ai_coverage,
            "total_ai_systems": len(all_ai_systems),
            "evaluated_ai_systems": len(evaluated_ai),
            "high_risk_ai_systems": len(high_risk_ai),
            "total_data_flows": len(all_flows),
            "compliant_data_flows": len(compliant_flows),
            "data_flows_with_gaps": len(gap_flows),
            "completed_audits": len(completed_audits),
            "pending_findings": len(pending_findings),
            "health_score": health_score,
        })

    def _calculate_health_score(
        self,
        open_risks,
        critical_risks,
        open_incidents,
        control_implementation_rate,
        data_flow_compliance_rate,
        ai_evaluation_rate,
    ):
        """
        Calculate composite security health score.

        Score components:
        - Risk posture (30%): Penalized for open/critical risks
        - Incident posture (20%): Penalized for open incidents
        - Control implementation (25%): Based on implementation rate
        - Data flow compliance (15%): Based on compliance rate
        - AI governance (10%): Based on evaluation rate
        """
        # Risk component (30 points max)
        risk_penalty = min(critical_risks * 5 + open_risks * 2, 30)
        risk_score = max(30 - risk_penalty, 0)

        # Incident component (20 points max)
        incident_penalty = min(open_incidents * 4, 20)
        incident_score = max(20 - incident_penalty, 0)

        # Control implementation (25 points max)
        control_score = control_implementation_rate * 0.25

        # Data flow compliance (15 points max)
        data_flow_score = data_flow_compliance_rate * 0.15

        # AI governance (10 points max)
        ai_score = ai_evaluation_rate * 0.10

        return min(
            risk_score + incident_score + control_score + data_flow_score + ai_score,
            100,
        )

    @api.model
    def get_current_kpis(self):
        """
        Get current KPI values without creating a snapshot.

        Returns a dictionary of current metrics suitable for API responses.
        """
        Risk = self.env["security.risk"]
        Incident = self.env["security.incident"]
        Asset = self.env["security.asset"]
        Control = self.env["security.control"]
        Framework = self.env["security.framework"]
        AISystem = self.env["ai.system"]
        DataFlow = self.env["security.data.flow"]

        thirty_days_ago = fields.Datetime.now() - timedelta(days=30)

        # Get framework coverage
        frameworks_coverage = {}
        for fw in Framework.search([("active", "=", True)]):
            frameworks_coverage[fw.code] = fw.coverage_percentage

        # Calculate metrics
        open_risks = Risk.search_count([("status", "in", ("open", "in_progress"))])
        critical_risks = Risk.search_count(
            [("risk_level", "=", "critical"), ("status", "in", ("open", "in_progress"))]
        )
        incidents_30d = Incident.search_count(
            [("detected_date", ">=", thirty_days_ago)]
        )
        total_assets = Asset.search_count([("in_scope", "=", True)])
        total_controls = Control.search_count([])
        implemented = Control.search_count(
            [("status", "in", ("implemented", "tested"))]
        )
        ai_systems = AISystem.search_count([("status", "=", "production")])
        high_risk_ai = AISystem.search_count(
            [("risk_level", "in", ("high", "unacceptable"))]
        )
        data_flow_gaps = DataFlow.search_count([("compliance_gap", "=", True)])

        # Calculate health score
        control_rate = (implemented / total_controls * 100) if total_controls else 0
        health_score = self._calculate_health_score(
            open_risks=open_risks,
            critical_risks=critical_risks,
            open_incidents=Incident.search_count([("status", "!=", "closed")]),
            control_implementation_rate=control_rate,
            data_flow_compliance_rate=100 - (data_flow_gaps * 10),  # Simplified
            ai_evaluation_rate=50,  # Default
        )

        return {
            "risks_open": open_risks,
            "risks_critical": critical_risks,
            "incidents_30d": incidents_30d,
            "assets_total": total_assets,
            "controls_implemented": implemented,
            "controls_total": total_controls,
            "ai_systems_production": ai_systems,
            "ai_systems_high_risk": high_risk_ai,
            "data_flow_gaps": data_flow_gaps,
            "health_score": round(health_score, 1),
            "framework_coverage": frameworks_coverage,
            "timestamp": fields.Datetime.now().isoformat(),
        }
