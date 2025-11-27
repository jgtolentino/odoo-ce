from odoo import fields, models


class IpaiWorkspace(models.Model):
    _inherit = "ipai.workspace"

    ppm_level = fields.Selection(
        [
            ("none", "Not PPM"),
            ("portfolio", "Portfolio"),
            ("program", "Program"),
            ("project", "Standalone Project"),
        ],
        string="PPM Level",
        default="none",
    )
    strategic_theme = fields.Char(
        string="Strategic Theme",
        help="e.g. Growth, Efficiency, Innovation.",
    )
    ppm_status = fields.Selection(
        [
            ("draft", "Draft"),
            ("planned", "Planned"),
            ("active", "Active"),
            ("on_hold", "On Hold"),
            ("closed", "Closed"),
        ],
        string="PPM Status",
        default="draft",
    )
    portfolio_owner_id = fields.Many2one(
        "res.users",
        string="Portfolio / Program Owner",
    )
    risk_score = fields.Float(
        string="Risk Score",
        help="0–100 risk score (higher means more risk).",
    )
    roi_projection = fields.Float(
        string="ROI Projection (%)",
        help="Projected ROI percentage for this workspace.",
    )
