from odoo import fields, models


class Project(models.Model):
    _inherit = "project.project"

    ppm_workspace_id = fields.Many2one(
        "ipai.workspace",
        string="PPM Workspace",
        help="Portfolio/program workspace that governs this project.",
    )
    ppm_alignment = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
        ],
        string="Strategic Alignment",
        help="Qualitative alignment to portfolio strategy.",
    )
    ppm_priority = fields.Selection(
        [
            ("3", "Low"),
            ("2", "Medium"),
            ("1", "High"),
        ],
        string="PPM Priority",
        default="2",
        help="1=High, 2=Medium, 3=Low.",
    )
