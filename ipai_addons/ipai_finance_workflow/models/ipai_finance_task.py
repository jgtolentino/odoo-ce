# -*- coding: utf-8 -*-
from odoo import api, fields, models

class IpaiFinanceTask(models.Model):
    _name = "ipai.finance.task"
    _description = "Finance Workflow Task (RACI)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_end DESC, sequence, id"

    name = fields.Char(required=True, tracking=True)
    description = fields.Text()
    sequence = fields.Integer(default=10)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, required=True)
    workspace_id = fields.Many2one("ipai.workspace", string="Workspace")
    project_id = fields.Many2one("project.project", string="Project")
    
    workstream = fields.Selection([
        ("month_end", "Month-End Closing"),
        ("tax_filing", "Tax Filing (BIR)"),
        ("reporting", "Management Reporting"),
        ("treasury", "Treasury / Cash"),
        ("audit", "Audit / Compliance"),
        ("project", "Project / PPM"),
        ("ad_hoc", "Ad-hoc"),
    ], string="Workstream", required=True, default="month_end", tracking=True)
    
    task_type = fields.Selection([
        ("recurring", "Recurring"),
        ("bir_filing", "BIR Filing"),
        ("project", "Project Task"),
        ("one_off", "One-Off"),
    ], string="Task Type", required=True, default="recurring")
    
    level = fields.Selection([
        ("goal", "Goal"),
        ("outcome", "Outcome"),
        ("objective", "Objective"),
        ("workstream", "Workstream"),
        ("task", "Task"),
        ("subtask", "Sub-task"),
    ], string="WBS Level", default="task")
    
    parent_id = fields.Many2one("ipai.finance.task", string="Parent Task", index=True)
    child_ids = fields.One2many("ipai.finance.task", "parent_id", string="Sub-tasks")
    wbs_code = fields.Char(string="WBS Code")
    
    frequency = fields.Selection([
        ("monthly", "Monthly"),
        ("quarterly", "Quarterly"),
        ("annual", "Annual"),
        ("ad_hoc", "Ad-hoc"),
    ], string="Frequency", default="monthly")
    
    period_start = fields.Date(string="Period Start")
    period_end = fields.Date(string="Period End")
    planned_start = fields.Datetime(string="Planned Start")
    planned_end = fields.Datetime(string="Planned End")
    actual_start = fields.Datetime(string="Actual Start")
    actual_end = fields.Datetime(string="Actual End")
    due_date = fields.Date(string="Due Date")
    
    stage_id = fields.Many2one("ipai.finance.stage", string="Stage", tracking=True)
    status = fields.Selection([
        ("draft", "Draft"),
        ("in_progress", "In Progress"),
        ("waiting_review", "Waiting Review"),
        ("completed", "Completed"),
        ("blocked", "Blocked"),
        ("cancelled", "Cancelled"),
    ], string="Status", default="draft", tracking=True)
    
    health = fields.Selection([
        ("on_track", "On Track"),
        ("at_risk", "At Risk"),
        ("off_track", "Off Track"),
    ], string="Health", default="on_track", tracking=True)
    
    progress = fields.Float(string="% Complete", digits=(3, 1))
    
    # RACI via ipai.person
    responsible_id = fields.Many2one("ipai.person", string="Responsible (R)", tracking=True)
    accountable_id = fields.Many2one("ipai.person", string="Accountable (A)", tracking=True)
    consulted_ids = fields.Many2many("ipai.person", "ipai_finance_task_consulted_rel", "task_id", "person_id", string="Consulted (C)")
    informed_ids = fields.Many2many("ipai.person", "ipai_finance_task_informed_rel", "task_id", "person_id", string="Informed (I)")
    
    responsible_user_id = fields.Many2one("res.users", string="Responsible User", compute="_compute_responsible_user", store=False)
    
    dependency_ids = fields.Many2many("ipai.finance.task", "ipai_finance_task_dependency_rel", "task_id", "dependency_id", string="Predecessors")
    
    bir_form = fields.Selection([
        ("1601c", "1601-C"),
        ("0619e", "0619-E"),
        ("2550m", "2550-M"),
        ("2550q", "2550-Q"),
        ("1702q", "1702-Q"),
        ("other", "Other"),
    ], string="BIR Form")
    
    legal_deadline = fields.Date(string="BIR Legal Deadline")
    evidences = fields.Text(string="Evidence / References")
    
    is_overdue = fields.Boolean(string="Overdue", compute="_compute_overdue", store=False)
    child_progress = fields.Float(string="Children % Complete", compute="_compute_child_progress", digits=(3, 1))
    
    checklist_ids = fields.One2many("ipai.task.checklist", "task_id", string="Checklist")
    
    @api.depends("responsible_id")
    def _compute_responsible_user(self):
        for rec in self:
            rec.responsible_user_id = rec.responsible_id.odoo_user_id if rec.responsible_id else False
    
    @api.depends("due_date", "status")
    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_overdue = bool(rec.due_date and rec.status not in ("completed", "cancelled") and rec.due_date < today)
    
    @api.depends("child_ids.progress", "child_ids.level")
    def _compute_child_progress(self):
        for rec in self:
            children = rec.child_ids.filtered(lambda t: t.level in ("task", "subtask"))
            rec.child_progress = sum(children.mapped("progress")) / len(children) if children else 0.0
    
    @api.onchange("stage_id")
    def _onchange_stage_id_set_status(self):
        for rec in self:
            if rec.stage_id and rec.stage_id.status_on_entry:
                rec.status = rec.stage_id.status_on_entry
