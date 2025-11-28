# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MarketingBrand(models.Model):
    _name = 'ipai.marketing.brand'
    _description = 'Marketing Brand'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Brand Name', required=True, tracking=True)
    code = fields.Char(string='Brand Code', help='Short identifier for the brand')
    partner_id = fields.Many2one('res.partner', string='Client', tracking=True)

    description = fields.Text(string='Brand Description')
    industry = fields.Selection([
        ('fmcg', 'FMCG'),
        ('retail', 'Retail'),
        ('tech', 'Technology'),
        ('finance', 'Financial Services'),
        ('healthcare', 'Healthcare'),
        ('automotive', 'Automotive'),
        ('telecom', 'Telecommunications'),
        ('other', 'Other'),
    ], string='Industry', default='other')

    # Brand assets
    logo = fields.Binary(string='Brand Logo')
    brand_guidelines_url = fields.Char(string='Brand Guidelines URL')

    # Relationships
    campaign_ids = fields.One2many('ipai.marketing.campaign', 'brand_id', string='Campaigns')
    campaign_count = fields.Integer(compute='_compute_campaign_count', string='Campaigns')

    # Status
    active = fields.Boolean(default=True)
    state = fields.Selection([
        ('prospect', 'Prospect'),
        ('active', 'Active Client'),
        ('on_hold', 'On Hold'),
        ('churned', 'Churned'),
    ], string='Status', default='prospect', tracking=True)

    @api.depends('campaign_ids')
    def _compute_campaign_count(self):
        for brand in self:
            brand.campaign_count = len(brand.campaign_ids)

    def action_view_campaigns(self):
        """Open campaigns for this brand."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Campaigns - {self.name}',
            'res_model': 'ipai.marketing.campaign',
            'view_mode': 'tree,form,kanban',
            'domain': [('brand_id', '=', self.id)],
            'context': {'default_brand_id': self.id},
        }
