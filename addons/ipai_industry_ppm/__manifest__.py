{
    "name": "InsightPulse PPM & WBS Industry Pack",
    "summary": "Clarity-style portfolio management and MS Project-style WBS on top of Workspaces & Projects",
    "version": "18.0.1.0.0",
    "category": "Project",
    "license": "LGPL-3",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "depends": [
        "ipai_workspace_core",  # your Workspaces app
        "project",
        "hr_timesheet",
        "sale_management",
    ],
    "data": [
        "security/ppm_security.xml",
        "security/ir.model.access.csv",
        "views/ppm_workspace_views.xml",
        "views/ppm_project_views.xml",
        "views/ppm_task_wbs_views.xml",
        "views/ppm_menu.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # JS/CSS hooks later if needed
        ],
    },
    "installable": True,
    "application": False,
}
