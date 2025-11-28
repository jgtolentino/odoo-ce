# -*- coding: utf-8 -*-
from odoo import models, fields, api


class FinancePerson(models.Model):
    _name = 'ipai.finance.person'
    _description = 'Finance Team Directory'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'

    code = fields.Char(string='Code', required=True, tracking=True, help="e.g. CKVC, RIM")
    name = fields.Char(string='Name', required=True, tracking=True)
    email = fields.Char(string='Email', tracking=True)

    # Contact fields for alerts/calls
    phone = fields.Char(string='Phone', tracking=True)
    mobile = fields.Char(string='Mobile', tracking=True, help='Primary contact for urgent alerts')

    role = fields.Selection([
        ('staff', 'Staff'),
        ('supervisor', 'Supervisor'),
        ('senior_supervisor', 'Senior Supervisor'),
        ('manager', 'Manager'),
        ('director', 'Director')
    ], string='Role', default='staff', tracking=True)

    user_id = fields.Many2one('res.users', string='Odoo User')
    active = fields.Boolean(default=True)

    display_name = fields.Char(compute='_compute_display_name', store=True)

    # Statistics
    deadline_count = fields.Integer(compute='_compute_deadline_count', string='Assigned Deadlines')

    @api.depends('code', 'name')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"[{record.code}] {record.name}" if record.code else record.name

    def _compute_deadline_count(self):
        Deadline = self.env['finance.bir.deadline']
        for person in self:
            person.deadline_count = Deadline.search_count([
                '|', '|',
                ('responsible_prep_id', '=', person.id),
                ('responsible_review_id', '=', person.id),
                ('responsible_approval_id', '=', person.id),
            ])

    def action_view_deadlines(self):
        """View all BIR deadlines assigned to this person."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Deadlines - {self.name}',
            'res_model': 'finance.bir.deadline',
            'view_mode': 'list,form,calendar',
            'domain': [
                '|', '|',
                ('responsible_prep_id', '=', self.id),
                ('responsible_review_id', '=', self.id),
                ('responsible_approval_id', '=', self.id),
            ],
        }

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Personnel code must be unique!')
    ]
