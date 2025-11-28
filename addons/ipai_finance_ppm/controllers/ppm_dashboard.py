# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from datetime import date
import json


class FinancePPMDashboard(http.Controller):
    """HTTP controller for Finance PPM ECharts dashboard"""

    @http.route("/ipai/finance/ppm", type="http", auth="user", website=True)
    def ppm_dashboard(self, **kwargs):
        """
        Main PPM dashboard route with ECharts visualizations

        Charts:
        1. BIR Timeline (Gantt-style showing deadlines)
        2. Completion vs Deadline (Bar chart)
        3. Status Distribution (Pie chart)
        """
        # Fetch BIR deadlines using the correct model
        bir_deadlines = request.env["finance.bir.deadline"].sudo().search(
            [], order="deadline_date asc"
        )

        # Prepare chart data
        chart_data = []
        for bir in bir_deadlines:
            # Calculate completion percentage based on state
            completion_map = {
                'pending': 0,
                'in_progress': 33,
                'submitted': 66,
                'filed': 100,
            }
            completion = completion_map.get(bir.state, 0)

            chart_data.append({
                "form": bir.name,
                "period": bir.period_covered or "",
                "filing_deadline": bir.deadline_date.isoformat() if bir.deadline_date else None,
                "prep_deadline": bir.target_prep_date.isoformat() if bir.target_prep_date else None,
                "review_deadline": bir.target_report_approval_date.isoformat() if bir.target_report_approval_date else None,
                "approval_deadline": bir.target_payment_approval_date.isoformat() if bir.target_payment_approval_date else None,
                "completion": completion,
                "status": bir.state or "pending",
                "supervisor": bir.responsible_prep_id.name if bir.responsible_prep_id else "Unassigned",
                "reviewer": bir.responsible_review_id.name if bir.responsible_review_id else "Unassigned",
                "approver": bir.responsible_approval_id.name if bir.responsible_approval_id else "Unassigned",
            })

        # Calculate status distribution
        status_counts = {}
        for bir in bir_deadlines:
            status = bir.state or "pending"
            status_counts[status] = status_counts.get(status, 0) + 1

        status_data = [
            {"name": status.replace("_", " ").title(), "value": count}
            for status, count in status_counts.items()
        ]

        return request.render("ipai_finance_ppm.ppm_dashboard_template", {
            "chart_data": json.dumps(chart_data),
            "status_data": json.dumps(status_data),
            "today": date.today().isoformat(),
            "schedule_count": len(bir_deadlines),
        })
