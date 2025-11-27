# -*- coding: utf-8 -*-
from odoo import api, fields, models

class IpaiTaskChecklist(models.Model):
    _name = "ipai.task.checklist"
    _description = "Finance Task Checklist Item"
    _order = "sequence, id"

    task_id = fields.Many2one("ipai.finance.task", string="Finance Task", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    name = fields.Char("Checklist item", required=True)
    
    role = fields.Selection([
        ("prep", "Preparation"),
        ("review", "Review"),
        ("approve", "Approval"),
    ], string="Activity Role")
    
    employee_code = fields.Char("Employee Code")
    person_id = fields.Many2one("ipai.person", string="Assigned Person")
    user_id = fields.Many2one("res.users", string="Assigned user")
    planned_date = fields.Date("Target date")
    done = fields.Boolean("Done")
    done_date = fields.Datetime("Done at")
    
    @api.onchange("done")
    def _onchange_done_set_date(self):
        for rec in self:
            if rec.done and not rec.done_date:
                rec.done_date = fields.Datetime.now()
            elif not rec.done:
                rec.done_date = False
