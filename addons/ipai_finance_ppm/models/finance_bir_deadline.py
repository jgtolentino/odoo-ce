# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)


class FinanceBIRDeadline(models.Model):
    _name = 'finance.bir.deadline'
    _description = 'BIR Tax Filing Deadline'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'deadline_date asc'
    _rec_name = 'display_name'

    name = fields.Char(string="BIR Form", required=True, tracking=True)
    period_covered = fields.Char(string="Period Covered", tracking=True)
    deadline_date = fields.Date(string="Filing Deadline", required=True, tracking=True)

    # Descriptive info
    description = fields.Text(string="Description")
    form_type = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
        ('one_time', 'One-Time'),
    ], string="Form Type", default='monthly')

    # SOP Document Link
    sop_document_id = fields.Many2one(
        'finance.bir.sop',
        string='SOP Document',
        help='Standard Operating Procedure for this BIR form'
    )

    # Process Targets (computed fields)
    target_prep_date = fields.Date(
        string="Target: Preparation",
        compute="_compute_targets",
        store=True,
        help="4 business days before the BIR deadline"
    )
    target_report_approval_date = fields.Date(
        string="Target: Report Approval",
        compute="_compute_targets",
        store=True,
        help="2 business days before the BIR deadline"
    )
    target_payment_approval_date = fields.Date(
        string="Target: Payment Approval",
        compute="_compute_targets",
        store=True,
        help="1 business day before the BIR deadline"
    )

    # Responsibility assignments
    responsible_prep_id = fields.Many2one('ipai.finance.person', string='Prep By')
    responsible_review_id = fields.Many2one('ipai.finance.person', string='Review By')
    responsible_approval_id = fields.Many2one('ipai.finance.person', string='Approve By')

    # Status tracking
    state = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('filed', 'Filed'),
    ], string="Status", default='pending', tracking=True)

    active = fields.Boolean(default=True)

    display_name = fields.Char(compute='_compute_display_name', store=True)

    @api.depends('name', 'period_covered')
    def _compute_display_name(self):
        for record in self:
            if record.period_covered:
                record.display_name = f"{record.name} - {record.period_covered}"
            else:
                record.display_name = record.name or ''

    @api.depends('deadline_date')
    def _compute_targets(self):
        """Compute target dates based on the filing deadline.

        - Preparation: 4 days before deadline
        - Report Approval: 2 days before deadline
        - Payment Approval: 1 day before deadline
        """
        for record in self:
            if record.deadline_date:
                record.target_prep_date = record.deadline_date - timedelta(days=4)
                record.target_report_approval_date = record.deadline_date - timedelta(days=2)
                record.target_payment_approval_date = record.deadline_date - timedelta(days=1)
            else:
                record.target_prep_date = False
                record.target_report_approval_date = False
                record.target_payment_approval_date = False

    def action_mark_in_progress(self):
        """Mark the deadline as in progress."""
        self.write({'state': 'in_progress'})

    def action_mark_submitted(self):
        """Mark the deadline as submitted."""
        self.write({'state': 'submitted'})

    def action_mark_filed(self):
        """Mark the deadline as filed."""
        self.write({'state': 'filed'})

    @api.model
    def get_upcoming_deadlines(self, days=14):
        """Get all deadlines due within the specified number of days."""
        today = fields.Date.today()
        end_date = today + timedelta(days=days)
        return self.search([
            ('deadline_date', '>=', today),
            ('deadline_date', '<=', end_date),
            ('state', 'not in', ['filed']),
        ])

    # -------------------------------------------------------------------------
    # Activity & Reminder Automation
    # -------------------------------------------------------------------------

    def action_schedule_activities(self):
        """Create scheduled activities for all responsible persons."""
        self.ensure_one()
        _logger.info(
            '[BIR Deadline %s] action_schedule_activities called | '
            'deadline_id=%d, name=%s, deadline_date=%s',
            self.id, self.id, self.name, self.deadline_date
        )

        try:
            activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
            if not activity_type:
                activity_type = self.env['mail.activity.type'].search([('name', 'ilike', 'To Do')], limit=1)
                _logger.debug('[BIR Deadline %s] Fallback activity_type search result: %s', self.id, activity_type)

            if not activity_type:
                _logger.error(
                    '[BIR Deadline %s] FAILED: No activity type found | '
                    'Checked: mail.mail_activity_data_todo and "To Do" search',
                    self.id
                )
                raise UserError(_('No activity type found. Please configure mail activity types.'))

            activities_created = 0

            # Schedule Preparation activity
            if self.responsible_prep_id and self.responsible_prep_id.user_id and self.target_prep_date:
                _logger.debug(
                    '[BIR Deadline %s] Scheduling prep activity for user_id=%d, date=%s',
                    self.id, self.responsible_prep_id.user_id.id, self.target_prep_date
                )
                self._create_activity(
                    activity_type,
                    self.responsible_prep_id.user_id,
                    self.target_prep_date,
                    _('Prepare %s filing for %s') % (self.name, self.period_covered or 'this period')
                )
                activities_created += 1
            else:
                _logger.debug(
                    '[BIR Deadline %s] Skipping prep activity | prep_id=%s, user_id=%s, target_date=%s',
                    self.id, self.responsible_prep_id.id if self.responsible_prep_id else None,
                    self.responsible_prep_id.user_id.id if self.responsible_prep_id and self.responsible_prep_id.user_id else None,
                    self.target_prep_date
                )

            # Schedule Review activity
            if self.responsible_review_id and self.responsible_review_id.user_id and self.target_report_approval_date:
                _logger.debug(
                    '[BIR Deadline %s] Scheduling review activity for user_id=%d, date=%s',
                    self.id, self.responsible_review_id.user_id.id, self.target_report_approval_date
                )
                self._create_activity(
                    activity_type,
                    self.responsible_review_id.user_id,
                    self.target_report_approval_date,
                    _('Review %s for %s') % (self.name, self.period_covered or 'this period')
                )
                activities_created += 1

            # Schedule Approval activity
            if self.responsible_approval_id and self.responsible_approval_id.user_id and self.target_payment_approval_date:
                _logger.debug(
                    '[BIR Deadline %s] Scheduling approval activity for user_id=%d, date=%s',
                    self.id, self.responsible_approval_id.user_id.id, self.target_payment_approval_date
                )
                self._create_activity(
                    activity_type,
                    self.responsible_approval_id.user_id,
                    self.target_payment_approval_date,
                    _('Approve %s payment for %s') % (self.name, self.period_covered or 'this period')
                )
                activities_created += 1

            if activities_created:
                _logger.info('[BIR Deadline %s] Successfully created %d activities', self.id, activities_created)
                self.message_post(
                    body=_('Scheduled %d reminder activities for this BIR deadline.') % activities_created,
                    message_type='notification'
                )
            else:
                _logger.warning(
                    '[BIR Deadline %s] No activities created - check responsible persons have linked user accounts',
                    self.id
                )

            return activities_created

        except Exception as e:
            _logger.exception(
                '[BIR Deadline %s] EXCEPTION in action_schedule_activities | '
                'error_type=%s, error_msg=%s',
                self.id, type(e).__name__, str(e)
            )
            raise

    def _create_activity(self, activity_type, user, date_deadline, summary):
        """Helper to create a mail activity."""
        try:
            activity_vals = {
                'activity_type_id': activity_type.id,
                'res_model_id': self.env['ir.model']._get_id(self._name),
                'res_id': self.id,
                'user_id': user.id,
                'date_deadline': date_deadline,
                'summary': summary,
                'note': _('BIR Form: %s\nPeriod: %s\nFiling Deadline: %s') % (
                    self.name,
                    self.period_covered or 'N/A',
                    self.deadline_date.strftime('%Y-%m-%d') if self.deadline_date else 'N/A'
                ),
            }
            activity = self.env['mail.activity'].create(activity_vals)
            _logger.debug(
                '[BIR Deadline %s] Created activity id=%d for user=%s (id=%d)',
                self.id, activity.id, user.name, user.id
            )
            return activity
        except Exception as e:
            _logger.error(
                '[BIR Deadline %s] FAILED to create activity | '
                'user_id=%d, user_name=%s, date=%s, summary=%s, error=%s',
                self.id, user.id, user.name, date_deadline, summary, str(e)
            )
            raise

    def action_send_reminder(self):
        """Send immediate reminder notification to all responsible persons."""
        self.ensure_one()
        _logger.info(
            '[BIR Deadline %s] action_send_reminder called | '
            'name=%s, deadline_date=%s, state=%s',
            self.id, self.name, self.deadline_date, self.state
        )

        try:
            partners = []
            message_lines = []

            if self.responsible_prep_id:
                if self.responsible_prep_id.user_id and self.responsible_prep_id.user_id.partner_id:
                    partners.append(self.responsible_prep_id.user_id.partner_id.id)
                message_lines.append(_('Prep: %s (%s)') % (
                    self.responsible_prep_id.name,
                    self.responsible_prep_id.mobile or self.responsible_prep_id.email or 'No contact'
                ))

            if self.responsible_review_id:
                if self.responsible_review_id.user_id and self.responsible_review_id.user_id.partner_id:
                    partners.append(self.responsible_review_id.user_id.partner_id.id)
                message_lines.append(_('Review: %s (%s)') % (
                    self.responsible_review_id.name,
                    self.responsible_review_id.mobile or self.responsible_review_id.email or 'No contact'
                ))

            if self.responsible_approval_id:
                if self.responsible_approval_id.user_id and self.responsible_approval_id.user_id.partner_id:
                    partners.append(self.responsible_approval_id.user_id.partner_id.id)
                message_lines.append(_('Approve: %s (%s)') % (
                    self.responsible_approval_id.name,
                    self.responsible_approval_id.mobile or self.responsible_approval_id.email or 'No contact'
                ))

            _logger.debug(
                '[BIR Deadline %s] Building reminder | partners=%s, team_count=%d',
                self.id, partners, len(message_lines)
            )

            days_remaining = (self.deadline_date - fields.Date.today()).days if self.deadline_date else 0

            body = _('''
<p><strong>BIR Deadline Reminder</strong></p>
<p><strong>Form:</strong> %(form)s<br/>
<strong>Period:</strong> %(period)s<br/>
<strong>Deadline:</strong> %(deadline)s<br/>
<strong>Days Remaining:</strong> %(days)d days<br/>
<strong>Status:</strong> %(status)s</p>
<p><strong>Responsible Team:</strong></p>
<ul>%(team)s</ul>
''') % {
                'form': self.name,
                'period': self.period_covered or 'N/A',
                'deadline': self.deadline_date.strftime('%Y-%m-%d') if self.deadline_date else 'N/A',
                'days': days_remaining,
                'status': dict(self._fields['state'].selection).get(self.state, self.state),
                'team': ''.join(['<li>%s</li>' % line for line in message_lines]),
            }

            self.message_post(
                body=body,
                partner_ids=partners,
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
            )

            _logger.info(
                '[BIR Deadline %s] Reminder sent successfully | partners_notified=%d',
                self.id, len(partners)
            )
            return True

        except Exception as e:
            _logger.exception(
                '[BIR Deadline %s] EXCEPTION in action_send_reminder | '
                'error_type=%s, error_msg=%s',
                self.id, type(e).__name__, str(e)
            )
            raise

    @api.model
    def cron_send_deadline_alerts(self):
        """Cron job to send automated alerts for upcoming BIR deadlines.

        Runs daily and sends alerts for:
        - Deadlines in 7 days (warning)
        - Deadlines in 3 days (urgent)
        - Deadlines tomorrow (critical)
        - Overdue deadlines (escalation)
        """
        today = fields.Date.today()
        _logger.info(
            '[BIR Cron] cron_send_deadline_alerts started | today=%s',
            today
        )

        alerts_sent = 0
        errors = []

        # Critical: Tomorrow
        tomorrow = today + timedelta(days=1)
        critical_deadlines = self.search([
            ('deadline_date', '=', tomorrow),
            ('state', 'not in', ['filed']),
        ])
        _logger.info('[BIR Cron] Found %d CRITICAL deadlines (tomorrow=%s)', len(critical_deadlines), tomorrow)
        for deadline in critical_deadlines:
            try:
                deadline._send_alert_notification('critical', 1)
                alerts_sent += 1
                _logger.debug('[BIR Cron] Sent critical alert for deadline_id=%d, name=%s', deadline.id, deadline.name)
            except Exception as e:
                error_msg = f'deadline_id={deadline.id}, name={deadline.name}, error={str(e)}'
                errors.append(error_msg)
                _logger.error('[BIR Cron] FAILED critical alert | %s', error_msg)

        # Urgent: 3 days
        three_days = today + timedelta(days=3)
        urgent_deadlines = self.search([
            ('deadline_date', '=', three_days),
            ('state', 'not in', ['submitted', 'filed']),
        ])
        _logger.info('[BIR Cron] Found %d URGENT deadlines (3-day=%s)', len(urgent_deadlines), three_days)
        for deadline in urgent_deadlines:
            try:
                deadline._send_alert_notification('urgent', 3)
                alerts_sent += 1
                _logger.debug('[BIR Cron] Sent urgent alert for deadline_id=%d, name=%s', deadline.id, deadline.name)
            except Exception as e:
                error_msg = f'deadline_id={deadline.id}, name={deadline.name}, error={str(e)}'
                errors.append(error_msg)
                _logger.error('[BIR Cron] FAILED urgent alert | %s', error_msg)

        # Warning: 7 days
        seven_days = today + timedelta(days=7)
        warning_deadlines = self.search([
            ('deadline_date', '=', seven_days),
            ('state', '=', 'pending'),
        ])
        _logger.info('[BIR Cron] Found %d WARNING deadlines (7-day=%s)', len(warning_deadlines), seven_days)
        for deadline in warning_deadlines:
            try:
                deadline._send_alert_notification('warning', 7)
                alerts_sent += 1
                _logger.debug('[BIR Cron] Sent warning alert for deadline_id=%d, name=%s', deadline.id, deadline.name)
            except Exception as e:
                error_msg = f'deadline_id={deadline.id}, name={deadline.name}, error={str(e)}'
                errors.append(error_msg)
                _logger.error('[BIR Cron] FAILED warning alert | %s', error_msg)

        # Overdue: Past deadline not filed
        overdue_deadlines = self.search([
            ('deadline_date', '<', today),
            ('state', 'not in', ['filed']),
        ])
        _logger.info('[BIR Cron] Found %d OVERDUE deadlines', len(overdue_deadlines))
        for deadline in overdue_deadlines:
            try:
                days_overdue = (today - deadline.deadline_date).days
                deadline._send_alert_notification('overdue', -days_overdue)
                alerts_sent += 1
                _logger.debug(
                    '[BIR Cron] Sent overdue alert for deadline_id=%d, name=%s, days_overdue=%d',
                    deadline.id, deadline.name, days_overdue
                )
            except Exception as e:
                error_msg = f'deadline_id={deadline.id}, name={deadline.name}, error={str(e)}'
                errors.append(error_msg)
                _logger.error('[BIR Cron] FAILED overdue alert | %s', error_msg)

        # Summary logging
        if errors:
            _logger.warning(
                '[BIR Cron] COMPLETED WITH ERRORS | alerts_sent=%d, errors=%d | error_details: %s',
                alerts_sent, len(errors), '; '.join(errors)
            )
        else:
            _logger.info('[BIR Cron] COMPLETED SUCCESSFULLY | alerts_sent=%d', alerts_sent)

        return alerts_sent

    def _send_alert_notification(self, alert_level, days_remaining):
        """Send alert notification based on urgency level."""
        self.ensure_one()
        _logger.debug(
            '[BIR Deadline %s] _send_alert_notification | level=%s, days_remaining=%d',
            self.id, alert_level, days_remaining
        )

        alert_icons = {
            'warning': '⚠️',
            'urgent': '🔔',
            'critical': '🚨',
            'overdue': '❌',
        }
        alert_colors = {
            'warning': '#ffc107',
            'urgent': '#fd7e14',
            'critical': '#dc3545',
            'overdue': '#6c757d',
        }

        icon = alert_icons.get(alert_level, '📌')
        color = alert_colors.get(alert_level, '#007bff')

        if days_remaining > 0:
            time_msg = _('%d days remaining') % days_remaining
        elif days_remaining == 0:
            time_msg = _('Due TODAY!')
        else:
            time_msg = _('%d days OVERDUE') % abs(days_remaining)

        # Build contact list with phone numbers
        contacts = []
        for person, role in [
            (self.responsible_prep_id, 'Prep'),
            (self.responsible_review_id, 'Review'),
            (self.responsible_approval_id, 'Approve'),
        ]:
            if person:
                contact_info = person.mobile or person.phone or person.email or 'No contact'
                contacts.append(f'{role}: {person.name} ({contact_info})')

        body = _('''
<div style="border-left: 4px solid %(color)s; padding-left: 12px;">
<p><strong>%(icon)s BIR Deadline Alert - %(level)s</strong></p>
<p><strong>%(form)s</strong> - %(period)s</p>
<p>Filing Deadline: <strong>%(deadline)s</strong> (%(time_msg)s)</p>
<p><strong>Contact Team:</strong><br/>%(contacts)s</p>
</div>
''') % {
            'icon': icon,
            'level': alert_level.upper(),
            'color': color,
            'form': self.name,
            'period': self.period_covered or '',
            'deadline': self.deadline_date.strftime('%B %d, %Y') if self.deadline_date else 'N/A',
            'time_msg': time_msg,
            'contacts': '<br/>'.join(contacts) if contacts else 'No contacts assigned',
        }

        # Get partner IDs for @mention
        partner_ids = []
        for person in [self.responsible_prep_id, self.responsible_review_id, self.responsible_approval_id]:
            if person and person.user_id and person.user_id.partner_id:
                partner_ids.append(person.user_id.partner_id.id)

        if not partner_ids:
            _logger.warning(
                '[BIR Deadline %s] No partners found for @mention | '
                'prep=%s (user=%s), review=%s (user=%s), approve=%s (user=%s)',
                self.id,
                self.responsible_prep_id.name if self.responsible_prep_id else None,
                self.responsible_prep_id.user_id.id if self.responsible_prep_id and self.responsible_prep_id.user_id else None,
                self.responsible_review_id.name if self.responsible_review_id else None,
                self.responsible_review_id.user_id.id if self.responsible_review_id and self.responsible_review_id.user_id else None,
                self.responsible_approval_id.name if self.responsible_approval_id else None,
                self.responsible_approval_id.user_id.id if self.responsible_approval_id and self.responsible_approval_id.user_id else None,
            )

        try:
            self.message_post(
                body=body,
                partner_ids=partner_ids,
                message_type='notification',
                subtype_xmlid='mail.mt_comment',
            )
            _logger.debug(
                '[BIR Deadline %s] Alert notification sent | level=%s, partners=%s',
                self.id, alert_level, partner_ids
            )
        except Exception as e:
            _logger.error(
                '[BIR Deadline %s] FAILED to send alert notification | '
                'level=%s, partners=%s, error_type=%s, error_msg=%s',
                self.id, alert_level, partner_ids, type(e).__name__, str(e)
            )
            raise
