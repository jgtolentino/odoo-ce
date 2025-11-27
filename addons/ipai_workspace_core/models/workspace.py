# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date


class IpaiWorkspace(models.Model):
    _name = 'ipai.workspace'
    _description = 'IPAI Workspace'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # === Core Fields ===
    name = fields.Char(
        string='Workspace Name',
        required=True,
        tracking=True,
    )

    workspace_type = fields.Selection([
        ('accounting', 'Accounting Client'),
        ('brand', 'Marketing Brand'),
        ('campaign', 'Marketing Campaign'),
        ('generic', 'Generic Workspace'),
    ], string='Type', default='generic', required=True, tracking=True)

    description = fields.Text(string='Description')

    # === Status ===
    status = fields.Selection([
        ('onboarding', 'Onboarding'),
        ('active', 'Active'),
        ('at_risk', 'At Risk'),
        ('closed', 'Closed'),
    ], string='Status', default='onboarding', tracking=True)

    status_color = fields.Integer(
        string='Status Color',
        compute='_compute_status_color',
    )

    # === Relationships ===
    partner_id = fields.Many2one(
        'res.partner',
        string='Client/Partner',
        tracking=True,
    )

    parent_id = fields.Many2one(
        'ipai.workspace',
        string='Parent Workspace',
        domain="[('workspace_type', 'in', ['accounting', 'brand'])]",
    )

    child_ids = fields.One2many(
        'ipai.workspace',
        'parent_id',
        string='Child Workspaces',
    )

    # === Ownership ===
    owner_id = fields.Many2one(
        'res.users',
        string='Owner',
        default=lambda self: self.env.user,
        tracking=True,
    )

    member_ids = fields.Many2many(
        'res.users',
        'ipai_workspace_member_rel',
        'workspace_id',
        'user_id',
        string='Members',
    )

    # === Industry/Segment ===
    industry = fields.Selection([
        ('retail', 'Retail'),
        ('fmcg', 'FMCG'),
        ('technology', 'Technology'),
        ('healthcare', 'Healthcare'),
        ('finance', 'Finance'),
        ('manufacturing', 'Manufacturing'),
        ('services', 'Services'),
        ('other', 'Other'),
    ], string='Industry')

    tag_ids = fields.Many2many(
        'ipai.workspace.tag',
        string='Tags',
    )

    # === Accounting-specific Fields ===
    fiscal_year_end = fields.Selection([
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ], string='Fiscal Year End')

    next_closing_date = fields.Date(string='Next Closing Date')

    # === Campaign-specific Fields ===
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')
    budget = fields.Monetary(string='Budget', currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
    )

    # === Metrics ===
    task_count = fields.Integer(
        string='Tasks',
        compute='_compute_task_count',
    )

    # === Computed Fields ===
    display_type_badge = fields.Char(
        string='Type Badge',
        compute='_compute_display_type_badge',
    )

    next_date = fields.Date(
        string='Next Date',
        compute='_compute_next_date',
        store=True,
    )

    @api.depends('status')
    def _compute_status_color(self):
        color_map = {
            'onboarding': 4,  # blue
            'active': 10,     # green
            'at_risk': 3,     # yellow/orange
            'closed': 1,      # gray
        }
        for record in self:
            record.status_color = color_map.get(record.status, 0)

    @api.depends('workspace_type')
    def _compute_display_type_badge(self):
        badge_map = {
            'accounting': 'ACCOUNTING',
            'brand': 'BRAND',
            'campaign': 'CAMPAIGN',
            'generic': 'WORKSPACE',
        }
        for record in self:
            record.display_type_badge = badge_map.get(record.workspace_type, 'WORKSPACE')

    @api.depends('next_closing_date', 'start_date', 'end_date', 'workspace_type')
    def _compute_next_date(self):
        for record in self:
            if record.workspace_type == 'accounting':
                record.next_date = record.next_closing_date
            elif record.workspace_type == 'campaign':
                today = date.today()
                if record.start_date and record.start_date > today:
                    record.next_date = record.start_date
                else:
                    record.next_date = record.end_date
            else:
                record.next_date = False

    def _compute_task_count(self):
        for record in self:
            record.task_count = 0  # Placeholder - integrate with project module later


class IpaiWorkspaceTag(models.Model):
    _name = 'ipai.workspace.tag'
    _description = 'Workspace Tag'
    _order = 'name'

    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color')
