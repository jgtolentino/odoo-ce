# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProjectTask(models.Model):
    """Extend project.task to link to Finance PPM logframe and BIR schedule.

    Implements Clarity PPM hierarchy concepts:
    - Phase: Grouping of related tasks (via finance_phase_id)
    - Task: Standard project.task
    - To-Do: Subtask checklist items (via finance_todo_ids)
    - Milestone: Key deliverable dates (via finance_milestone)
    """
    _inherit = "project.task"

    # -------------------------------------------------------------------------
    # Clarity PPM Hierarchy Fields
    # -------------------------------------------------------------------------
    finance_phase_id = fields.Many2one(
        'ipai.finance.phase',
        string='Finance Phase',
        help='Clarity PPM Phase grouping for this task'
    )

    finance_milestone = fields.Boolean(
        string='Is Milestone',
        default=False,
        help='Mark as a key milestone in the project timeline'
    )

    finance_milestone_type = fields.Selection([
        ('deliverable', 'Deliverable'),
        ('checkpoint', 'Checkpoint'),
        ('approval', 'Approval Gate'),
        ('deadline', 'Regulatory Deadline'),
    ], string='Milestone Type')

    finance_todo_ids = fields.One2many(
        'ipai.finance.task.todo',
        'task_id',
        string='To-Do Checklist',
        help='Detailed checklist items (Clarity PPM To-Do concept)'
    )

    finance_todo_progress = fields.Float(
        string='To-Do Progress',
        compute='_compute_todo_progress',
        store=True,
        help='Percentage of completed to-do items'
    )

    # -------------------------------------------------------------------------
    # Finance-specific fields
    # -------------------------------------------------------------------------
    finance_code = fields.Char(
        string='Finance Code',
        help='Employee code like RIM, BOM, CKVC'
    )

    reviewer_id = fields.Many2one(
        'res.users',
        string='Reviewer/Consulted',
        help='Person responsible for reviewing the task'
    )

    approver_id = fields.Many2one(
        'res.users',
        string='Approver/Accountable',
        help='Person responsible for final approval'
    )

    finance_deadline_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
    ], string='Finance Deadline Type')

    # Link to finance person directory
    finance_person_id = fields.Many2one(
        'ipai.finance.person',
        string='Finance Person'
    )

    # Duration fields for finance workflow
    prep_duration = fields.Float(string='Prep Duration (Days)')
    review_duration = fields.Float(string='Review Duration (Days)')
    approval_duration = fields.Float(string='Approval Duration (Days)')

    # Finance categories
    finance_category = fields.Selection([
        ('foundation_corp', 'Foundation & Corp'),
        ('revenue_wip', 'Revenue/WIP'),
        ('vat_tax', 'VAT & Tax Reporting'),
        ('working_capital', 'Working Capital'),
        ('compliance', 'Compliance'),
        ('administrative', 'Administrative'),
    ], string='Finance Category')

    finance_logframe_id = fields.Many2one(
        "ipai.finance.logframe",
        string="Logframe Entry",
        help="Link to Finance Logical Framework objective"
    )

    bir_schedule_id = fields.Many2one(
        "ipai.finance.bir_schedule",
        string="BIR Form",
        help="Link to BIR Filing Schedule"
    )

    # Computed fields for dashboard visibility
    is_finance_ppm = fields.Boolean(
        compute="_compute_is_finance_ppm",
        store=True,
        string="Is Finance PPM Task"
    )

    @api.depends('finance_todo_ids', 'finance_todo_ids.is_done')
    def _compute_todo_progress(self):
        for task in self:
            todos = task.finance_todo_ids
            if todos:
                done_count = len(todos.filtered(lambda t: t.is_done))
                task.finance_todo_progress = (done_count / len(todos)) * 100
            else:
                task.finance_todo_progress = 0.0

    @api.depends(
        'finance_logframe_id', 'bir_schedule_id',
        'finance_code', 'finance_person_id', 'finance_phase_id'
    )
    def _compute_is_finance_ppm(self):
        for task in self:
            task.is_finance_ppm = bool(
                task.finance_logframe_id or
                task.bir_schedule_id or
                task.finance_code or
                task.finance_person_id or
                task.finance_phase_id
            )


class FinancePhase(models.Model):
    """Clarity PPM Phase - Top level grouping for tasks.

    Example phases for Finance SSC:
    - Monthly Close Preparation
    - Tax Filing (BIR)
    - Regional Reporting
    - Year-End Close
    """
    _name = 'ipai.finance.phase'
    _description = 'Finance PPM Phase (Clarity PPM)'
    _order = 'sequence, start_date, id'

    name = fields.Char(string='Phase Name', required=True)
    code = fields.Char(string='Phase Code', help='Short identifier (e.g., MC-01, BIR-Q1)')
    sequence = fields.Integer(string='Sequence', default=10)

    description = fields.Text(string='Description')
    project_id = fields.Many2one(
        'project.project',
        string='Project',
        help='Parent project for this phase'
    )

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    phase_type = fields.Selection([
        ('monthly_close', 'Monthly Close'),
        ('quarterly_close', 'Quarterly Close'),
        ('annual_close', 'Annual Close'),
        ('tax_filing', 'Tax Filing'),
        ('reporting', 'Reporting'),
        ('audit', 'Audit Preparation'),
        ('other', 'Other'),
    ], string='Phase Type', default='other')

    task_ids = fields.One2many(
        'project.task',
        'finance_phase_id',
        string='Tasks'
    )

    task_count = fields.Integer(
        string='Task Count',
        compute='_compute_task_count',
        store=True
    )

    progress = fields.Float(
        string='Progress %',
        compute='_compute_progress',
        store=True
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft')

    responsible_id = fields.Many2one(
        'ipai.finance.person',
        string='Phase Lead'
    )

    @api.depends('task_ids')
    def _compute_task_count(self):
        for phase in self:
            phase.task_count = len(phase.task_ids)

    @api.depends('task_ids', 'task_ids.stage_id')
    def _compute_progress(self):
        for phase in self:
            tasks = phase.task_ids
            if tasks:
                # Count completed tasks (those in folded/done stages)
                completed = len(tasks.filtered(lambda t: t.stage_id.fold))
                phase.progress = (completed / len(tasks)) * 100
            else:
                phase.progress = 0.0

    def action_view_tasks(self):
        """Open the tasks associated with this phase."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Tasks - {self.name}',
            'res_model': 'project.task',
            'view_mode': 'list,form',
            'domain': [('finance_phase_id', '=', self.id)],
            'context': {'default_finance_phase_id': self.id},
        }

    def action_start(self):
        """Mark phase as active."""
        self.write({'state': 'active'})

    def action_complete(self):
        """Mark phase as completed."""
        self.write({'state': 'completed'})


class FinanceTaskTodo(models.Model):
    """Clarity PPM To-Do - Checklist items within a task.

    Provides granular tracking of sub-steps within a task.
    """
    _name = 'ipai.finance.task.todo'
    _description = 'Finance Task To-Do Item (Clarity PPM)'
    _order = 'sequence, id'

    name = fields.Char(string='To-Do', required=True)
    sequence = fields.Integer(string='Sequence', default=10)

    task_id = fields.Many2one(
        'project.task',
        string='Parent Task',
        required=True,
        ondelete='cascade'
    )

    is_done = fields.Boolean(string='Done', default=False)
    done_date = fields.Datetime(string='Completed At')
    done_by_id = fields.Many2one('res.users', string='Completed By')

    assignee_id = fields.Many2one(
        'ipai.finance.person',
        string='Assignee',
        help='Person responsible for this to-do item'
    )

    due_date = fields.Date(string='Due Date')
    notes = fields.Text(string='Notes')

    @api.onchange('is_done')
    def _onchange_is_done(self):
        if self.is_done:
            self.done_date = fields.Datetime.now()
            self.done_by_id = self.env.user
        else:
            self.done_date = False
            self.done_by_id = False

    def action_mark_done(self):
        """Mark to-do item as done."""
        self.write({
            'is_done': True,
            'done_date': fields.Datetime.now(),
            'done_by_id': self.env.user.id,
        })

    def action_mark_undone(self):
        """Mark to-do item as not done."""
        self.write({
            'is_done': False,
            'done_date': False,
            'done_by_id': False,
        })
