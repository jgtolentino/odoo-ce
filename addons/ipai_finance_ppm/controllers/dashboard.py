# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
from datetime import datetime, timedelta


class FinancePPMDashboard(http.Controller):
    """
    ECharts Dashboard Controller for Finance PPM

    Endpoints:
    - /ipai/finance/ppm - Main dashboard
    - /ipai/finance/ppm/api/bir - JSON API for BIR data
    - /ipai/finance/ppm/api/logframe - JSON API for logframe data
    """

    @http.route('/ipai/finance/ppm', type='http', auth='user', website=True)
    def ppm_dashboard(self):
        """Main Finance PPM dashboard with ECharts"""

        # Fetch BIR schedule data
        bir_schedules = request.env['ipai.finance.bir_schedule'].search([
            ('filing_deadline', '>=', datetime.now().date()),
        ], order='filing_deadline asc')

        # Fetch Finance PPM tasks
        tasks = request.env['project.task'].search([
            ('is_finance_ppm', '=', True)
        ])

        # Fetch logframe objectives
        logframe_items = request.env['ipai.finance.logframe'].search([])

        # Prepare BIR deadline timeline data (bar chart)
        bir_timeline_data = []
        bir_categories = []
        for bir in bir_schedules:
            bir_categories.append(f"{bir.form_code} {bir.period}")
            # Color code based on status
            color = {
                'not_started': '#ff6b6b',  # Red
                'in_progress': '#ffa500',  # Orange
                'submitted': '#4ecdc4',    # Teal
                'filed': '#95e1d3',        # Green
                'late': '#f38181'          # Dark Red
            }.get(bir.status, '#cccccc')

            bir_timeline_data.append({
                'value': (bir.filing_deadline - datetime.now().date()).days,
                'itemStyle': {'color': color},
                'label': {'show': True, 'formatter': bir.status.replace('_', ' ').title()}
            })

        # Prepare completion tracking data (percentage bar chart)
        completion_data = []
        for bir in bir_schedules:
            completion_data.append({
                'name': f"{bir.form_code} {bir.period}",
                'value': bir.completion_pct,
                'itemStyle': {
                    'color': '#95e1d3' if bir.completion_pct >= 80 else (
                        '#ffa500' if bir.completion_pct >= 50 else '#ff6b6b'
                    )
                }
            })

        # Prepare status distribution (pie chart)
        status_counts = {}
        for bir in bir_schedules:
            status_counts[bir.status] = status_counts.get(bir.status, 0) + 1

        status_pie_data = [
            {'value': count, 'name': status.replace('_', ' ').title()}
            for status, count in status_counts.items()
        ]

        # Prepare logframe overview (task count by level)
        logframe_levels = {}
        for item in logframe_items:
            level_label = dict(item._fields['level'].selection).get(item.level, item.level)
            logframe_levels[level_label] = logframe_levels.get(level_label, 0) + item.task_count

        logframe_data = [
            {'level': level, 'count': count}
            for level, count in logframe_levels.items()
        ]

        # KPI calculations
        total_bir_forms = len(bir_schedules)
        ontime_filings = len(bir_schedules.filtered(lambda b: b.status == 'filed'))
        at_risk = len(bir_schedules.filtered(lambda b: b.status == 'in_progress'))
        late_filings = len(bir_schedules.filtered(lambda b: b.status == 'late'))

        compliance_rate = (ontime_filings / total_bir_forms * 100) if total_bir_forms > 0 else 0

        return request.render('ipai_finance_ppm.dashboard_template', {
            'bir_categories': json.dumps(bir_categories),
            'bir_timeline_data': json.dumps(bir_timeline_data),
            'completion_data': json.dumps(completion_data),
            'status_pie_data': json.dumps(status_pie_data),
            'logframe_data': json.dumps(logframe_data),
            # KPIs
            'kpi_total': total_bir_forms,
            'kpi_ontime': ontime_filings,
            'kpi_compliance_rate': round(compliance_rate, 1),
            'kpi_atrisk': at_risk,
            'kpi_late': late_filings,
        })

    @http.route('/ipai/finance/ppm/api/bir', type='json', auth='user')
    def api_bir_data(self):
        """JSON API for BIR schedule data"""
        bir_schedules = request.env['ipai.finance.bir_schedule'].search([])

        return [{
            'id': bir.id,
            'form_code': bir.form_code,
            'period': bir.period,
            'filing_deadline': bir.filing_deadline.isoformat() if bir.filing_deadline else None,
            'status': bir.status,
            'completion_pct': bir.completion_pct,
            'prep_deadline': bir.prep_deadline.isoformat() if bir.prep_deadline else None,
            'review_deadline': bir.review_deadline.isoformat() if bir.review_deadline else None,
            'approval_deadline': bir.approval_deadline.isoformat() if bir.approval_deadline else None,
        } for bir in bir_schedules]

    @http.route('/ipai/finance/ppm/api/logframe', type='json', auth='user')
    def api_logframe_data(self):
        """JSON API for logframe data"""
        logframe_items = request.env['ipai.finance.logframe'].search([])

        return [{
            'id': item.id,
            'name': item.name,
            'level': item.level,
            'indicator': item.indicator,
            'target_value': item.target_value,
            'task_count': item.task_count,
            'parent_id': item.parent_id.id if item.parent_id else None,
        } for item in logframe_items]
