# -*- coding: utf-8 -*-
from odoo import fields, models

class ProjectTask(models.Model):
    _inherit = "project.task"

    finance_checklist_ids = fields.One2many("ipai.task.checklist", "task_id", string="Finance Checklist")
