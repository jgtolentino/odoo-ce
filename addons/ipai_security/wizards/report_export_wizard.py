# -*- coding: utf-8 -*-
# Copyright 2024 InsightPulseAI
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""
Report Export Wizard
====================

Wizard for exporting security posture reports.
"""
import base64
import json

from odoo import api, fields, models


class ReportExportWizard(models.TransientModel):
    """
    Transient model for exporting security reports.

    Supports JSON and CSV export of security posture data.
    """

    _name = "security.report.export.wizard"
    _description = "Security Report Export Wizard"

    report_type = fields.Selection(
        [
            ("posture", "Security Posture Summary"),
            ("assets", "Asset Inventory"),
            ("risks", "Risk Register"),
            ("controls", "Controls Matrix"),
            ("ai_systems", "AI Systems Register"),
            ("data_flows", "Data Flow Mapping"),
            ("dpa_readiness", "PH DPA Readiness"),
        ],
        string="Report Type",
        default="posture",
        required=True,
    )
    format = fields.Selection(
        [
            ("json", "JSON"),
            ("csv", "CSV"),
        ],
        string="Format",
        default="json",
        required=True,
    )
    include_frameworks = fields.Many2many(
        "security.framework",
        string="Frameworks",
        help="Filter by frameworks (leave empty for all)",
    )
    include_risks = fields.Boolean(
        string="Include Risks",
        default=True,
    )
    include_controls = fields.Boolean(
        string="Include Controls",
        default=True,
    )
    include_ai_systems = fields.Boolean(
        string="Include AI Systems",
        default=True,
    )
    # Output
    state = fields.Selection(
        [
            ("draft", "Configure"),
            ("done", "Download"),
        ],
        string="State",
        default="draft",
    )
    file_data = fields.Binary(
        string="Report File",
        readonly=True,
    )
    file_name = fields.Char(
        string="File Name",
        readonly=True,
    )

    def action_generate(self):
        """Generate the export report."""
        self.ensure_one()

        # Generate report data based on type
        if self.report_type == "posture":
            data = self._generate_posture_report()
        elif self.report_type == "assets":
            data = self._generate_assets_report()
        elif self.report_type == "risks":
            data = self._generate_risks_report()
        elif self.report_type == "controls":
            data = self._generate_controls_report()
        elif self.report_type == "ai_systems":
            data = self._generate_ai_systems_report()
        elif self.report_type == "data_flows":
            data = self._generate_data_flows_report()
        elif self.report_type == "dpa_readiness":
            data = self._generate_dpa_report()
        else:
            data = {}

        # Format output
        if self.format == "json":
            content = json.dumps(data, indent=2, default=str)
            file_name = f"security_{self.report_type}_{fields.Date.today()}.json"
        else:
            content = self._dict_to_csv(data)
            file_name = f"security_{self.report_type}_{fields.Date.today()}.csv"

        self.write({
            "state": "done",
            "file_data": base64.b64encode(content.encode("utf-8")),
            "file_name": file_name,
        })

        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def _generate_posture_report(self):
        """Generate security posture summary."""
        kpis = self.env["security.kpi"].get_current_kpis()
        return {
            "report_type": "Security Posture Summary",
            "generated_at": fields.Datetime.now().isoformat(),
            "kpis": kpis,
            "frameworks": self._get_framework_summary(),
        }

    def _generate_assets_report(self):
        """Generate asset inventory report."""
        assets = self.env["security.asset"].search([("in_scope", "=", True)])
        return {
            "report_type": "Asset Inventory",
            "generated_at": fields.Datetime.now().isoformat(),
            "total_assets": len(assets),
            "assets": [
                {
                    "name": a.name,
                    "code": a.code,
                    "type": a.asset_type,
                    "environment": a.environment,
                    "risk_level": a.risk_level,
                    "handles_pii": a.handles_pii,
                    "owner": a.owner_user_id.name if a.owner_user_id else None,
                }
                for a in assets
            ],
        }

    def _generate_risks_report(self):
        """Generate risk register report."""
        domain = []
        if self.include_frameworks:
            domain.append(("framework_ids", "in", self.include_frameworks.ids))

        risks = self.env["security.risk"].search(domain)
        return {
            "report_type": "Risk Register",
            "generated_at": fields.Datetime.now().isoformat(),
            "total_risks": len(risks),
            "risks": [
                {
                    "reference": r.reference,
                    "title": r.name,
                    "category": r.risk_category,
                    "severity": r.severity,
                    "likelihood": r.likelihood,
                    "inherent_score": r.inherent_risk_score,
                    "residual_score": r.residual_risk_score,
                    "risk_level": r.risk_level,
                    "status": r.status,
                    "owner": r.owner_id.name if r.owner_id else None,
                }
                for r in risks
            ],
        }

    def _generate_controls_report(self):
        """Generate controls matrix report."""
        domain = []
        if self.include_frameworks:
            domain.append(("framework_id", "in", self.include_frameworks.ids))

        controls = self.env["security.control"].search(domain)
        return {
            "report_type": "Controls Matrix",
            "generated_at": fields.Datetime.now().isoformat(),
            "total_controls": len(controls),
            "controls": [
                {
                    "code": c.code,
                    "title": c.name,
                    "framework": c.framework_id.code,
                    "type": c.control_type,
                    "status": c.status,
                    "test_result": c.test_result,
                    "last_test_date": c.last_test_date.isoformat() if c.last_test_date else None,
                    "owner": c.owner_id.name if c.owner_id else None,
                }
                for c in controls
            ],
        }

    def _generate_ai_systems_report(self):
        """Generate AI systems register report."""
        systems = self.env["ai.system"].search([])
        return {
            "report_type": "AI Systems Register",
            "generated_at": fields.Datetime.now().isoformat(),
            "total_systems": len(systems),
            "ai_systems": [
                {
                    "name": s.name,
                    "code": s.code,
                    "type": s.system_type,
                    "provider": s.provider,
                    "models": s.models_used,
                    "risk_level": s.risk_level,
                    "eval_status": s.eval_status,
                    "handles_pii": s.handles_pii,
                    "status": s.status,
                }
                for s in systems
            ],
        }

    def _generate_data_flows_report(self):
        """Generate data flow mapping report."""
        flows = self.env["security.data.flow"].search([])
        return {
            "report_type": "Data Flow Mapping",
            "generated_at": fields.Datetime.now().isoformat(),
            "total_flows": len(flows),
            "data_flows": [
                {
                    "reference": f.reference,
                    "source": f.source_asset_id.name,
                    "target": f.target_asset_id.name,
                    "lawful_basis": f.lawful_basis_id.name if f.lawful_basis_id else None,
                    "purpose": f.purpose,
                    "contains_pii": f.contains_pii,
                    "encrypted": f.is_encrypted,
                    "compliance_gap": f.compliance_gap,
                    "status": f.status,
                }
                for f in flows
            ],
        }

    def _generate_dpa_report(self):
        """Generate PH DPA readiness report."""
        dpa_framework = self.env["security.framework"].search(
            [("code", "=", "DPA")], limit=1
        )
        pii_assets = self.env["security.asset"].search([("handles_pii", "=", True)])
        pii_flows = self.env["security.data.flow"].search([("contains_pii", "=", True)])

        return {
            "report_type": "PH DPA Readiness Assessment",
            "generated_at": fields.Datetime.now().isoformat(),
            "dpa_coverage": dpa_framework.coverage_percentage if dpa_framework else 0,
            "pii_processing_assets": len(pii_assets),
            "pii_data_flows": len(pii_flows),
            "flows_with_gaps": len(pii_flows.filtered(lambda f: f.compliance_gap)),
            "data_categories_in_use": len(
                self.env["security.data.category"].search([
                    ("dpa_classification", "in", ("personal", "sensitive_personal"))
                ])
            ),
        }

    def _get_framework_summary(self):
        """Get summary of all active frameworks."""
        frameworks = self.env["security.framework"].search([("active", "=", True)])
        return [
            {
                "code": f.code,
                "name": f.name,
                "coverage": f.coverage_percentage,
                "in_scope": f.in_scope,
                "control_count": f.control_count,
            }
            for f in frameworks
        ]

    def _dict_to_csv(self, data):
        """Convert dictionary to CSV string."""
        import io
        import csv

        output = io.StringIO()

        if "risks" in data:
            items = data["risks"]
        elif "assets" in data:
            items = data["assets"]
        elif "controls" in data:
            items = data["controls"]
        elif "ai_systems" in data:
            items = data["ai_systems"]
        elif "data_flows" in data:
            items = data["data_flows"]
        else:
            items = [data]

        if items:
            writer = csv.DictWriter(output, fieldnames=items[0].keys())
            writer.writeheader()
            writer.writerows(items)

        return output.getvalue()
