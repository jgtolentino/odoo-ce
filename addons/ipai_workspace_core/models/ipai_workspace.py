from odoo import api, fields, models


class IpaiWorkspace(models.Model):
    _name = "ipai.workspace"
    _description = "InsightPulse Workspace"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(
        string="Name",
        required=True,
        tracking=True,
    )

    workspace_type = fields.Selection(
        [
            ("generic", "Generic"),
            ("accounting_client", "Accounting Client"),
            ("marketing_brand", "Marketing Brand"),
            ("marketing_campaign", "Marketing Campaign"),
            ("ppm_portfolio", "PPM Portfolio"),
            ("ppm_program", "PPM Program"),
        ],
        string="Workspace Type",
        default="generic",
        required=True,
        tracking=True,
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Client / Partner",
        tracking=True,
    )

    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        tracking=True,
        default=lambda self: self.env.user,
    )

    member_ids = fields.Many2many(
        "res.users",
        "ipai_workspace_member_rel",
        "workspace_id",
        "user_id",
        string="Members",
    )

    description = fields.Html(
        string="Description",
        sanitize=True,
        help="Rich description of this workspace (scope, notes, references).",
    )

    color = fields.Integer(
        string="Color Index",
        help="Color index used in kanban views.",
    )

    active = fields.Boolean(
        string="Active",
        default=True,
        help="Uncheck to archive this workspace.",
    )

    # Basic computed stats placeholders you can extend later
    project_count = fields.Integer(
        string="Project Count",
        compute="_compute_project_count",
    )

    last_activity_date = fields.Datetime(
        string="Last Activity",
        compute="_compute_last_activity",
    )

    @api.depends("id")
    def _compute_project_count(self):
        """Extend later: count linked projects per workspace."""
        for ws in self:
            ws.project_count = 0

    @api.depends("id")
    def _compute_last_activity(self):
        """Extend later: last log note / task / message."""
        for ws in self:
            ws.last_activity_date = False
