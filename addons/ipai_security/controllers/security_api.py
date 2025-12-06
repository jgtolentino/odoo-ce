# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Security API Controller
=======================

JSON REST API endpoints for the Security & Compliance Workbench.
These endpoints are designed for agent access and automation.
"""
from odoo import http
from odoo.http import request


class SecurityAPIController(http.Controller):
    """
    HTTP controller for security API endpoints.

    All endpoints require authentication (auth='user') and return JSON.
    These endpoints are designed for internal use by AI agents and
    automation systems.
    """

    @http.route("/api/security/kpis", type="json", auth="user", methods=["POST"])
    def get_kpis(self):
        """
        Get current security KPIs.

        Returns aggregated metrics for the security dashboard including:
        - Open risk counts
        - Recent incident counts
        - Framework coverage percentages
        - Overall health score

        Returns:
            dict: Current KPI values
        """
        SecurityKPI = request.env["security.kpi"]
        return SecurityKPI.get_current_kpis()

    @http.route("/api/security/kpis/snapshot", type="json", auth="user", methods=["POST"])
    def capture_kpi_snapshot(self):
        """
        Capture a new KPI snapshot.

        Creates a permanent record of current metrics for historical tracking.

        Returns:
            dict: Snapshot ID and timestamp
        """
        SecurityKPI = request.env["security.kpi"]
        snapshot = SecurityKPI.capture_snapshot()
        return {
            "id": snapshot.id,
            "snapshot_date": snapshot.snapshot_date.isoformat(),
            "health_score": snapshot.health_score,
        }

    @http.route("/api/security/assets", type="json", auth="user", methods=["POST"])
    def get_assets(self, asset_type=None, environment=None, in_scope=None, limit=100, offset=0):
        """
        Get security assets.

        Args:
            asset_type: Filter by asset type (application, agent, droplet, etc.)
            environment: Filter by environment (production, staging, etc.)
            in_scope: Filter by compliance scope (True/False)
            limit: Maximum records to return (default 100)
            offset: Pagination offset

        Returns:
            dict: List of assets with pagination info
        """
        Asset = request.env["security.asset"]
        domain = []

        if asset_type:
            domain.append(("asset_type", "=", asset_type))
        if environment:
            domain.append(("environment", "=", environment))
        if in_scope is not None:
            domain.append(("in_scope", "=", in_scope))

        total = Asset.search_count(domain)
        assets = Asset.search(domain, limit=limit, offset=offset)

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "assets": [
                {
                    "id": a.id,
                    "name": a.name,
                    "code": a.code,
                    "asset_type": a.asset_type,
                    "environment": a.environment,
                    "status": a.status,
                    "risk_level": a.risk_level,
                    "handles_pii": a.handles_pii,
                    "in_scope": a.in_scope,
                    "owner": a.owner_user_id.name if a.owner_user_id else None,
                }
                for a in assets
            ],
        }

    @http.route("/api/security/risks", type="json", auth="user", methods=["POST"])
    def get_risks(self, status=None, risk_level=None, framework=None, limit=100, offset=0):
        """
        Get security risks.

        Args:
            status: Filter by status (open, in_progress, mitigated, etc.)
            risk_level: Filter by risk level (critical, high, medium, low)
            framework: Filter by framework code
            limit: Maximum records to return
            offset: Pagination offset

        Returns:
            dict: List of risks with pagination info
        """
        Risk = request.env["security.risk"]
        domain = []

        if status:
            domain.append(("status", "=", status))
        if risk_level:
            domain.append(("risk_level", "=", risk_level))
        if framework:
            domain.append(("framework_ids.code", "=", framework))

        total = Risk.search_count(domain)
        risks = Risk.search(domain, limit=limit, offset=offset)

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "risks": [
                {
                    "id": r.id,
                    "reference": r.reference,
                    "name": r.name,
                    "description": r.description,
                    "risk_category": r.risk_category,
                    "severity": r.severity,
                    "likelihood": r.likelihood,
                    "inherent_risk_score": r.inherent_risk_score,
                    "residual_risk_score": r.residual_risk_score,
                    "risk_level": r.risk_level,
                    "status": r.status,
                    "control_effectiveness": r.control_effectiveness,
                    "owner": r.owner_id.name if r.owner_id else None,
                }
                for r in risks
            ],
        }

    @http.route("/api/security/ai-systems", type="json", auth="user", methods=["POST"])
    def get_ai_systems(self, provider=None, risk_level=None, status=None, limit=100, offset=0):
        """
        Get AI systems.

        Args:
            provider: Filter by AI provider (anthropic, openai, etc.)
            risk_level: Filter by risk level
            status: Filter by status (production, development, etc.)
            limit: Maximum records to return
            offset: Pagination offset

        Returns:
            dict: List of AI systems with pagination info
        """
        AISystem = request.env["ai.system"]
        domain = []

        if provider:
            domain.append(("provider", "=", provider))
        if risk_level:
            domain.append(("risk_level", "=", risk_level))
        if status:
            domain.append(("status", "=", status))

        total = AISystem.search_count(domain)
        systems = AISystem.search(domain, limit=limit, offset=offset)

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "ai_systems": [
                {
                    "id": s.id,
                    "name": s.name,
                    "code": s.code,
                    "system_type": s.system_type,
                    "provider": s.provider,
                    "models_used": s.models_used,
                    "risk_level": s.risk_level,
                    "eval_status": s.eval_status,
                    "handles_pii": s.handles_pii,
                    "status": s.status,
                    "intended_use": s.intended_use,
                }
                for s in systems
            ],
        }

    @http.route("/api/security/incidents", type="json", auth="user", methods=["POST"])
    def get_incidents(self, severity=None, status=None, since=None, limit=100, offset=0):
        """
        Get security incidents.

        Args:
            severity: Filter by severity
            status: Filter by status
            since: Filter incidents detected since this date (ISO format)
            limit: Maximum records to return
            offset: Pagination offset

        Returns:
            dict: List of incidents with pagination info
        """
        Incident = request.env["security.incident"]
        domain = []

        if severity:
            domain.append(("severity", "=", severity))
        if status:
            domain.append(("status", "=", status))
        if since:
            domain.append(("detected_date", ">=", since))

        total = Incident.search_count(domain)
        incidents = Incident.search(domain, limit=limit, offset=offset)

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "incidents": [
                {
                    "id": i.id,
                    "reference": i.reference,
                    "name": i.name,
                    "incident_type": i.incident_type,
                    "severity": i.severity,
                    "status": i.status,
                    "detected_date": i.detected_date.isoformat() if i.detected_date else None,
                    "pii_involved": i.pii_involved,
                    "is_ai_related": i.is_ai_related,
                }
                for i in incidents
            ],
        }

    @http.route("/api/security/agent-summary", type="json", auth="user", methods=["POST"])
    def get_agent_summary(self):
        """
        Get security summary for AI agents.

        Returns a comprehensive summary suitable for AI agent consumption,
        answering questions like:
        - What is the current security posture?
        - Which agents access PH personal data?
        - Which SOC 2 controls are failing?

        Returns:
            dict: Agent-friendly security summary
        """
        kpis = request.env["security.kpi"].get_current_kpis()

        # Get PII-handling AI systems
        pii_ai_systems = request.env["ai.system"].search([
            ("handles_pii", "=", True),
            ("status", "=", "production"),
        ])

        # Get failing/untested SOC 2 controls
        soc2_issues = request.env["security.control"].search([
            ("framework_id.code", "=", "SOC2"),
            "|",
            ("status", "=", "not_implemented"),
            ("test_result", "=", "failed"),
        ])

        # Get compliance gaps in data flows
        data_flow_gaps = request.env["security.data.flow"].search([
            ("compliance_gap", "=", True),
        ])

        return {
            "posture_summary": {
                "health_score": kpis["health_score"],
                "assessment": self._assess_posture(kpis["health_score"]),
                "open_risks": kpis["risks_open"],
                "critical_risks": kpis["risks_critical"],
                "open_incidents": kpis.get("incidents_30d", 0),
            },
            "framework_coverage": kpis["framework_coverage"],
            "ai_systems_with_pii": [
                {
                    "name": s.name,
                    "provider": s.provider,
                    "risk_level": s.risk_level,
                    "data_categories": [c.name for c in s.data_category_ids],
                }
                for s in pii_ai_systems
            ],
            "soc2_control_issues": [
                {
                    "code": c.code,
                    "name": c.name,
                    "status": c.status,
                    "test_result": c.test_result,
                }
                for c in soc2_issues
            ],
            "data_flow_compliance_gaps": [
                {
                    "name": f.name,
                    "source": f.source_asset_id.name,
                    "target": f.target_asset_id.name,
                    "has_lawful_basis": bool(f.lawful_basis_id),
                    "is_encrypted": f.is_encrypted,
                }
                for f in data_flow_gaps
            ],
            "timestamp": kpis["timestamp"],
        }

    def _assess_posture(self, health_score):
        """Provide human-readable posture assessment."""
        if health_score >= 80:
            return "Good - Security posture is strong with minimal gaps"
        elif health_score >= 60:
            return "Fair - Some areas need attention but overall acceptable"
        elif health_score >= 40:
            return "Needs Improvement - Multiple areas require remediation"
        else:
            return "Critical - Significant security gaps exist requiring immediate action"

    @http.route("/api/security/report", type="http", auth="user", methods=["GET"])
    def generate_report(self, format="json"):
        """
        Generate security posture report.

        Args:
            format: Output format (json or pdf)

        Returns:
            Response with report data or file download
        """
        summary = self.get_agent_summary()

        if format == "json":
            return request.make_json_response(summary)
        else:
            # For PDF, we would use QWeb report - simplified for now
            return request.make_json_response({
                "error": "PDF export not yet implemented",
                "data": summary,
            })
