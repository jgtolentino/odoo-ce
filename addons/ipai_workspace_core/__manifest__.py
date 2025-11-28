# -*- coding: utf-8 -*-
{
    'name': 'IPAI Workspace Core',
    'version': '18.0.2.0.0',
    'category': 'Project Management',
    'summary': 'Notion-style Workspace Foundation with Clarity PPM Hierarchy',
    'description': """
IPAI Workspace Core - Notion-style Foundation
=============================================

Provides the foundational workspace model (ipai.workspace) implementing
Notion-style project organization with Broadcom Clarity PPM hierarchy.

This is the CORE foundation module that industry packs extend via _inherit.

Work Breakdown Structure:
------------------------
- Project (root container)
- Phase (WBS grouping via parent tasks)
- Milestone (zero-duration progress markers)
- Task (units of work with dependencies)
- To-Do Item (granular checklists)

Features:
---------
* Workspace model for Notion parity
* Clarity ID field for project tracking
* Health status indicators (Green/Yellow/Red)
* Baseline vs Actual variance tracking
* Phase progress rollup from child tasks
* Milestone gate workflows with approval
* Task dependencies (FS, SS, FF, SF)
* To-Do items with assignees and due dates
* Gantt chart visualization

OCA Dependencies:
-----------------
* project_key, project_category, project_wbs
* project_milestone, project_task_milestone
* project_task_dependency, project_task_checklist
* project_timeline, project_parent_task_filter

Canonical Module: 2 of 5
Part of InsightPulse ERP Target Image (Smart Delta Philosophy)

Author: InsightPulse AI
License: AGPL-3
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',
    'depends': [
        'project',
        'project_key',
        'project_category',
        'project_wbs',
        'project_parent_task_filter',
        'project_milestone',
        'project_task_milestone',
        'project_task_dependency',
        'project_task_checklist',
        'project_timeline',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/clarity_data.xml',
        'views/project_project_views.xml',
        'views/project_phase_views.xml',
        'views/project_milestone_views.xml',
        'views/project_task_views.xml',
        'views/project_menu.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
