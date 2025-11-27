# -*- coding: utf-8 -*-
from odoo import fields, models

class IpaiFinanceStage(models.Model):
    _name = "ipai.finance.stage"
    _description = "Finance Workflow Stage"
    _order = "sequence, id"

    name = fields.Char(required=True)
    code = fields.Char(help="Short code, e.g. PREP, REVIEW, APPROVE")
    category = fields.Selection([
        ("month_end", "Month-End Closing"),
        ("tax_filing", "Tax Filing (BIR)"),
        ("reporting", "Management Reporting"),
        ("treasury", "Treasury / Cash"),
        ("project", "Project / PPM"),
        ("other", "Other"),
    ], string="Category", required=True, default="month_end")
    
    stage_type = fields.Selection([
        ("prep", "Preparation"),
        ("review", "Review"),
        ("approve", "Approval"),
        ("file_pay", "File/Pay"),
        ("reconcile", "Reconciliation"),
        ("report", "Reporting"),
        ("close", "Period Close"),
        ("other", "Other"),
    ], string="Stage Type", default="other")
    
    sequence = fields.Integer(default=10)
    is_default = fields.Boolean(string="Default Stage")
    fold = fields.Boolean(string="Fold in Kanban")
    status_on_entry = fields.Selection([
        ("draft", "Draft"),
        ("in_progress", "In Progress"),
        ("waiting_review", "Waiting Review"),
        ("completed", "Completed"),
        ("blocked", "Blocked"),
    ], string="Status on Entry", default="in_progress")
    
    task_ids = fields.One2many("ipai.finance.task", "stage_id", string="Tasks")
