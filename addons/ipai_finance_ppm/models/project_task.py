# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProjectTask(models.Model):
    """
    Extended project.task with Finance PPM fields

    Adds:
    - Link to Logframe objective
    - Link to BIR schedule
    - Computed field to filter Finance PPM tasks
    """
    _inherit = 'project.task'

    finance_logframe_id = fields.Many2one(
        'ipai.finance.logframe',
        string='Logframe Objective',
        ondelete='set null',
        help='Link to Finance logical framework objective'
    )

    bir_schedule_id = fields.Many2one(
        'ipai.finance.bir_schedule',
        string='BIR Schedule',
        ondelete='set null',
        help='Link to BIR filing schedule'
    )

    is_finance_ppm = fields.Boolean(
        string='Finance PPM Task',
        compute='_compute_is_finance_ppm',
        store=True,
        help='Computed field: True if task is linked to logframe or BIR schedule'
    )

    @api.depends('finance_logframe_id', 'bir_schedule_id')
    def _compute_is_finance_ppm(self):
        """Compute if task is part of Finance PPM"""
        for task in self:
            task.is_finance_ppm = bool(task.finance_logframe_id or task.bir_schedule_id)
