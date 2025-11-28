# -*- coding: utf-8 -*-
from odoo import models, fields, api


class FinanceBIRSOP(models.Model):
    """Standard Operating Procedures for BIR Form Filing.

    Based on OCA document_page pattern for knowledge management.
    Each SOP provides step-by-step procedures for filing specific BIR forms.
    """
    _name = 'finance.bir.sop'
    _description = 'BIR Filing SOP Document'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, form_code'

    name = fields.Char(string='SOP Title', required=True, tracking=True)
    form_code = fields.Char(
        string='BIR Form Code',
        required=True,
        help='e.g., 1601-C, 2550M, 1702Q'
    )
    sequence = fields.Integer(default=10)

    # Classification
    form_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
        ('one_time', 'One-Time'),
    ], string="Form Type", default='monthly')

    category = fields.Selection([
        ('withholding', 'Withholding Tax'),
        ('income', 'Income Tax'),
        ('vat', 'VAT'),
        ('percentage', 'Percentage Tax'),
        ('documentary', 'Documentary Stamp'),
        ('other', 'Other'),
    ], string='Tax Category', default='other')

    # Content
    description = fields.Text(string='Description')
    purpose = fields.Html(string='Purpose', help='Why this form is required')

    # Step-by-step procedure
    procedure_html = fields.Html(
        string='Filing Procedure',
        help='Detailed step-by-step instructions for filing'
    )

    # Checklist items
    checklist_ids = fields.One2many(
        'finance.bir.sop.checklist',
        'sop_id',
        string='Checklist Items'
    )

    # Requirements and references
    requirements = fields.Html(string='Requirements', help='Documents/data needed')
    bir_link = fields.Char(string='BIR Reference Link')
    attachments_count = fields.Integer(compute='_compute_attachments_count')

    # Timeline guidance
    prep_days = fields.Integer(
        string='Prep Days Before Deadline',
        default=4,
        help='Recommended days to start preparation'
    )
    review_days = fields.Integer(
        string='Review Days Before Deadline',
        default=2,
        help='Days needed for review process'
    )

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('obsolete', 'Obsolete'),
    ], string='Status', default='draft', tracking=True)

    approved_by_id = fields.Many2one('res.users', string='Approved By')
    approved_date = fields.Date(string='Approved Date')

    # Version tracking
    version = fields.Char(string='Version', default='1.0')
    last_review_date = fields.Date(string='Last Review Date')
    next_review_date = fields.Date(string='Next Review Date')

    active = fields.Boolean(default=True)

    def _compute_attachments_count(self):
        Attachment = self.env['ir.attachment']
        for sop in self:
            sop.attachments_count = Attachment.search_count([
                ('res_model', '=', self._name),
                ('res_id', '=', sop.id),
            ])

    def action_approve(self):
        """Approve the SOP document."""
        self.write({
            'state': 'approved',
            'approved_by_id': self.env.user.id,
            'approved_date': fields.Date.today(),
        })

    def action_set_draft(self):
        """Set SOP back to draft for revision."""
        self.write({'state': 'draft'})

    def action_view_attachments(self):
        """View all attachments for this SOP."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Attachments - {self.name}',
            'res_model': 'ir.attachment',
            'view_mode': 'list,form',
            'domain': [
                ('res_model', '=', self._name),
                ('res_id', '=', self.id),
            ],
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
            },
        }


class FinanceBIRSOPChecklist(models.Model):
    """Checklist items for BIR SOP procedures."""
    _name = 'finance.bir.sop.checklist'
    _description = 'BIR SOP Checklist Item'
    _order = 'sequence, id'

    sop_id = fields.Many2one(
        'finance.bir.sop',
        string='SOP',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Checklist Item', required=True)
    description = fields.Text(string='Details')
    responsible_role = fields.Selection([
        ('staff', 'Staff'),
        ('supervisor', 'Supervisor'),
        ('senior_supervisor', 'Senior Supervisor'),
        ('manager', 'Manager'),
        ('director', 'Director'),
    ], string='Responsible Role')
    is_mandatory = fields.Boolean(string='Mandatory', default=True)
