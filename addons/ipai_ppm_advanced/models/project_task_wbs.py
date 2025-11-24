from collections import defaultdict
from typing import Dict, List

from odoo import api, fields, models


class ProjectTaskWBS(models.Model):
    _inherit = 'project.task'

    wbs_code = fields.Char(
        string="WBS ID",
        compute="_compute_wbs_code",
        store=True,
        help="Work Breakdown Structure number automatically generated from the task hierarchy.",
    )

    @api.depends(
        'project_id',
        'parent_id',
        'sequence',
        'parent_id.child_ids.sequence',
        'parent_id.child_ids.id',
    )
    def _compute_wbs_code(self) -> None:
        """Assign hierarchical WBS numbers (e.g., 1.2.3) per project with sibling-aware ordering."""
        tasks_by_project: Dict[int, List[models.Model]] = defaultdict(list)
        for task in self:
            if task.project_id:
                tasks_by_project[task.project_id.id].append(task)
            else:
                task.wbs_code = False

        for project_id, tasks in tasks_by_project.items():
            project_tasks = self.env['project.task'].search(
                [('project_id', '=', project_id)], order='parent_id, sequence, id'
            )
            child_map: Dict[int | bool, List[models.Model]] = defaultdict(list)
            for task in project_tasks:
                key = task.parent_id.id if task.parent_id else False
                child_map[key].append(task)

            for siblings in child_map.values():
                siblings.sort(key=lambda t: (t.sequence, t.id))

            wbs_values: Dict[int, str] = {}

            def _assign_codes(current_task: models.Model, prefix: str) -> None:
                wbs_values[current_task.id] = prefix
                for index, child in enumerate(child_map.get(current_task.id, []), start=1):
                    _assign_codes(child, f"{prefix}.{index}")

            for index, root in enumerate(child_map.get(False, []), start=1):
                _assign_codes(root, str(index))

            for task in tasks:
                task.wbs_code = wbs_values.get(task.id)
