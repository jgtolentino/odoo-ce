# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import timedelta
from odoo.exceptions import UserError


class FinanceBIRSchedule(models.Model):
    """
    BIR Filing Schedule with automated task creation

    Workflow:
    1. Create BIR form record with filing_deadline
    2. System auto-calculates internal deadlines (BIR - 4/2/1 days)
    3. Daily cron creates 3 tasks (prep, review, approval)
    4. Tasks linked to IM2 logframe objective
    """
    _name = 'ipai.finance.bir_schedule'
    _description = 'BIR Filing Schedule'
    _order = 'filing_deadline desc, form_code'

    name = fields.Char(
        string='Name',
        compute='_compute_name',
        store=True
    )

    form_code = fields.Selection([
        ('1601-C', '1601-C - Monthly Withholding Tax'),
        ('0619-E', '0619-E - Monthly Remittance - Expanded Withholding Tax'),
        ('2550Q', '2550Q - Quarterly Income Tax'),
        ('1702-RT', '1702-RT - Annual Income Tax Return'),
        ('1601-EQ', '1601-EQ - Quarterly Remittance - Expanded Withholding Tax'),
        ('1601-FQ', '1601-FQ - Quarterly Remittance - Final Withholding Tax'),
    ], string='BIR Form', required=True, help='BIR form code')

    period = fields.Char(
        string='Period',
        required=True,
        help='Tax period (e.g., "December 2025", "Q4 2025")'
    )

    filing_deadline = fields.Date(
        string='BIR Filing Deadline',
        required=True,
        help='Official BIR filing deadline'
    )

    prep_deadline = fields.Date(
        string='Preparation Deadline',
        compute='_compute_internal_deadlines',
        store=True,
        help='Internal deadline for preparation (BIR - 4 days)'
    )

    review_deadline = fields.Date(
        string='Review Deadline',
        compute='_compute_internal_deadlines',
        store=True,
        help='Internal deadline for review (BIR - 2 days)'
    )

    approval_deadline = fields.Date(
        string='Approval Deadline',
        compute='_compute_internal_deadlines',
        store=True,
        help='Internal deadline for approval (BIR - 1 day)'
    )

    responsible_prep = fields.Many2one(
        'res.users',
        string='Responsible (Prep)',
        help='Finance Supervisor responsible for preparation'
    )

    responsible_review = fields.Many2one(
        'res.users',
        string='Responsible (Review)',
        help='Senior Finance Manager responsible for review'
    )

    responsible_approval = fields.Many2one(
        'res.users',
        string='Responsible (Approval)',
        help='Finance Director responsible for approval'
    )

    status = fields.Selection([
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('filed', 'Filed'),
        ('late', 'Late'),
    ], string='Status', default='not_started', tracking=True)

    completion_pct = fields.Float(
        string='Completion %',
        compute='_compute_completion_pct',
        store=True,
        help='Percentage of completion based on task status'
    )

    task_prep_id = fields.Many2one(
        'project.task',
        string='Preparation Task',
        ondelete='set null'
    )

    task_review_id = fields.Many2one(
        'project.task',
        string='Review Task',
        ondelete='set null'
    )

    task_approval_id = fields.Many2one(
        'project.task',
        string='Approval Task',
        ondelete='set null'
    )

    logframe_id = fields.Many2one(
        'ipai.finance.logframe',
        string='Linked Logframe',
        help='IM2 objective for tax filing compliance'
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    @api.depends('form_code', 'period')
    def _compute_name(self):
        """Generate display name from form code and period"""
        for record in self:
            record.name = f"{record.form_code} - {record.period}"

    @api.depends('filing_deadline')
    def _compute_internal_deadlines(self):
        """Calculate internal deadlines (BIR - 4/2/1 days)"""
        for record in self:
            if record.filing_deadline:
                record.prep_deadline = record.filing_deadline - timedelta(days=4)
                record.review_deadline = record.filing_deadline - timedelta(days=2)
                record.approval_deadline = record.filing_deadline - timedelta(days=1)
            else:
                record.prep_deadline = False
                record.review_deadline = False
                record.approval_deadline = False

    @api.depends('task_prep_id.stage_id', 'task_review_id.stage_id', 'task_approval_id.stage_id')
    def _compute_completion_pct(self):
        """Compute completion percentage based on task stages"""
        for record in self:
            completed_count = 0
            total_tasks = 3

            if record.task_prep_id and record.task_prep_id.stage_id.is_closed:
                completed_count += 1

            if record.task_review_id and record.task_review_id.stage_id.is_closed:
                completed_count += 1

            if record.task_approval_id and record.task_approval_id.stage_id.is_closed:
                completed_count += 1

            record.completion_pct = (completed_count / total_tasks) * 100 if total_tasks > 0 else 0

    def action_create_tasks(self):
        """
        Create 3 project tasks (prep, review, approval) for this BIR form

        Called by:
        - Daily cron job (8AM)
        - Manual button click
        """
        self.ensure_one()

        # Find or create Finance PPM project
        project = self.env['project.project'].search([
            ('name', '=', 'Finance PPM')
        ], limit=1)

        if not project:
            raise UserError(_("Finance PPM project not found. Please create it first."))

        # Find IM2 logframe objective
        if not self.logframe_id:
            logframe_im2 = self.env['ipai.finance.logframe'].search([
                ('level', '=', 'im2')
            ], limit=1)
            if logframe_im2:
                self.logframe_id = logframe_im2

        # Create Preparation task
        if not self.task_prep_id:
            self.task_prep_id = self.env['project.task'].create({
                'name': f"{self.form_code} {self.period} - Preparation",
                'project_id': project.id,
                'user_ids': [(6, 0, [self.responsible_prep.id])] if self.responsible_prep else [],
                'date_deadline': self.prep_deadline,
                'description': f"Prepare {self.form_code} for {self.period}",
                'bir_schedule_id': self.id,
                'finance_logframe_id': self.logframe_id.id if self.logframe_id else False,
                'priority': '1',  # High priority
            })

        # Create Review task
        if not self.task_review_id:
            self.task_review_id = self.env['project.task'].create({
                'name': f"{self.form_code} {self.period} - Review",
                'project_id': project.id,
                'user_ids': [(6, 0, [self.responsible_review.id])] if self.responsible_review else [],
                'date_deadline': self.review_deadline,
                'description': f"Review {self.form_code} for {self.period}",
                'bir_schedule_id': self.id,
                'finance_logframe_id': self.logframe_id.id if self.logframe_id else False,
                'priority': '1',
                'depend_on_ids': [(6, 0, [self.task_prep_id.id])],  # Depends on prep task
            })

        # Create Approval task
        if not self.task_approval_id:
            self.task_approval_id = self.env['project.task'].create({
                'name': f"{self.form_code} {self.period} - Approval",
                'project_id': project.id,
                'user_ids': [(6, 0, [self.responsible_approval.id])] if self.responsible_approval else [],
                'date_deadline': self.approval_deadline,
                'description': f"Approve {self.form_code} for {self.period}",
                'bir_schedule_id': self.id,
                'finance_logframe_id': self.logframe_id.id if self.logframe_id else False,
                'priority': '1',
                'depend_on_ids': [(6, 0, [self.task_review_id.id])],  # Depends on review task
            })

        return True

    def action_mark_filed(self):
        """Mark BIR form as filed and update completion to 100%"""
        self.ensure_one()
        self.write({
            'status': 'filed',
            'completion_pct': 100.0
        })

    @api.model
    def _cron_sync_bir_tasks(self):
        """
        Daily cron job to create tasks for upcoming BIR forms

        Schedule: 8:00 AM daily
        """
        # Find BIR forms due in next 30 days that don't have tasks yet
        upcoming_forms = self.search([
            ('filing_deadline', '>=', fields.Date.today()),
            ('filing_deadline', '<=', fields.Date.today() + timedelta(days=30)),
            '|', ('task_prep_id', '=', False),
            '|', ('task_review_id', '=', False),
            ('task_approval_id', '=', False),
        ])

        for bir_form in upcoming_forms:
            try:
                bir_form.action_create_tasks()
            except Exception as e:
                _logger.error(f"Failed to create tasks for {bir_form.name}: {str(e)}")

        return True
