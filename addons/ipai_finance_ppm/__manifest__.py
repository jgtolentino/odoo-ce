# -*- coding: utf-8 -*-
{
    'name': 'InsightPulse Finance PPM',
    'version': '18.0.1.0.0',
    'category': 'Project',
    'summary': 'PMBOK-compliant Finance task matrix with WBS, dependencies, and ECharts dashboards',
    'description': """
        Finance Project Portfolio Management
        =====================================

        Features:
        - Logical Framework (Logframe) tracking with hierarchical levels
        - BIR Filing Schedule with automated task creation
        - ECharts interactive dashboards (Gantt, KPIs, status tracking)
        - PMBOK-compliant WBS codes and dependency management
        - Critical path analysis with CPM scheduling
        - Multi-employee Finance SSC operations

        Integrates with:
        - Project (core)
        - Knowledge (documentation)
        - Spreadsheet (reporting)
        - To-Do (quick tasks)
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'project',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/email_templates.xml',
        'data/ir_cron_data.xml',
        'data/finance_logframe_seed.xml',
        'data/finance_bir_schedule_seed.xml',
        'views/dashboard_template.xml',
        'views/finance_logframe_views.xml',
        'views/bir_schedule_views.xml',
        'views/project_task_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
