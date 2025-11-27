from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    parent_task_id = fields.Many2one(
        "project.task",
        string="Parent Task",
        index=True,
        domain="[('project_id', '=', project_id)]",
        help="Parent task for WBS hierarchy within the same project.",
    )
    child_task_ids = fields.One2many(
        "project.task",
        "parent_task_id",
        string="Subtasks",
    )

    wbs_code = fields.Char(
        string="WBS Code",
        index=True,
        help="Manually editable WBS code (e.g. 1.2.3).",
    )
    wbs_auto = fields.Char(
        string="Auto WBS",
        compute="_compute_wbs_auto",
        store=True,
        help="System-generated WBS path based on hierarchy (for sorting).",
    )
    wbs_sequence = fields.Integer(
        string="WBS Sequence",
        default=10,
        help="Ordering at each level; combined with auto WBS for full ordering.",
    )

    @api.depends("parent_task_id", "wbs_sequence", "parent_task_id.wbs_auto")
    def _compute_wbs_auto(self):
        for task in self:
            if task.parent_task_id and task.parent_task_id.wbs_auto:
                task.wbs_auto = "%s.%03d" % (
                    task.parent_task_id.wbs_auto,
                    task.wbs_sequence or 0,
                )
            else:
                # Top-level task
                task.wbs_auto = "%03d" % (task.wbs_sequence or 0)
