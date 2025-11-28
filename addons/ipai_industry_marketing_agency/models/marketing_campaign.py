# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MarketingCampaign(models.Model):
    _name = 'ipai.marketing.campaign'
    _description = 'Marketing Campaign'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_date desc'

    name = fields.Char(string='Campaign Name', required=True, tracking=True)
    code = fields.Char(string='Campaign Code')
    brand_id = fields.Many2one('ipai.marketing.brand', string='Brand', required=True, tracking=True)
    partner_id = fields.Many2one(related='brand_id.partner_id', string='Client', store=True)

    # Timeline
    start_date = fields.Date(string='Start Date', tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)

    # Description
    description = fields.Text(string='Campaign Brief')
    objectives = fields.Text(string='Objectives')
    target_audience = fields.Text(string='Target Audience')

    # Budget
    budget_allocated = fields.Monetary(string='Budget Allocated', currency_field='currency_id')
    budget_spent = fields.Monetary(string='Budget Spent', currency_field='currency_id')
    budget_remaining = fields.Monetary(compute='_compute_budget_remaining', string='Budget Remaining')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                   default=lambda self: self.env.company.currency_id)

    # Campaign type
    campaign_type = fields.Selection([
        ('brand_awareness', 'Brand Awareness'),
        ('lead_gen', 'Lead Generation'),
        ('product_launch', 'Product Launch'),
        ('seasonal', 'Seasonal Campaign'),
        ('event', 'Event Marketing'),
        ('content', 'Content Marketing'),
        ('social', 'Social Media'),
        ('other', 'Other'),
    ], string='Campaign Type', default='other')

    # Channels
    channel_ids = fields.Many2many('ipai.marketing.channel', string='Marketing Channels')

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)

    # Linked project (Clarity PPM integration)
    project_id = fields.Many2one('project.project', string='Linked Project')

    active = fields.Boolean(default=True)

    @api.depends('budget_allocated', 'budget_spent')
    def _compute_budget_remaining(self):
        for campaign in self:
            campaign.budget_remaining = campaign.budget_allocated - campaign.budget_spent

    def action_start_planning(self):
        self.write({'state': 'planning'})

    def action_activate(self):
        self.write({'state': 'active'})

    def action_pause(self):
        self.write({'state': 'paused'})

    def action_complete(self):
        self.write({'state': 'completed'})


class MarketingChannel(models.Model):
    _name = 'ipai.marketing.channel'
    _description = 'Marketing Channel'
    _order = 'name'

    name = fields.Char(string='Channel Name', required=True)
    channel_type = fields.Selection([
        ('digital', 'Digital'),
        ('traditional', 'Traditional'),
        ('experiential', 'Experiential'),
    ], string='Channel Type', default='digital')
    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)
