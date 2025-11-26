# Finance PPM Automation Guide

Complete guide for setting up automated BIR deadline alerts and email notifications.

## Email Templates Created

Three email templates are included:

### 1. **7-Day Warning Alert** (`email_template_bir_7day_warning`)
- **Subject**: ⚠️ BIR Deadline Alert: {FORM} {PERIOD} Due in 7 Days
- **Recipients**: Preparation + Review responsible persons
- **Trigger**: BIR deadline is 7 days away
- **Content**:
  - BIR form details with color-coded status
  - Completion progress bar
  - Internal deadlines (prep, review, approval)
  - Action required message
  - Direct link to BIR form in Odoo

### 2. **Overdue Alert** (`email_template_bir_overdue`)
- **Subject**: 🚨 URGENT: BIR Deadline OVERDUE - {FORM} {PERIOD}
- **Recipients**: Approval responsible person (Finance Director)
- **CC**: Preparation + Review responsible persons
- **Trigger**: BIR deadline has passed and form not filed
- **Content**:
  - Critical alert header
  - Days overdue counter
  - Current status and completion %
  - Immediate action checklist
  - Direct link to BIR form in Odoo

### 3. **Task Completion Reminder** (`email_template_bir_task_reminder`)
- **Subject**: 📋 Reminder: Complete BIR Tasks for {FORM} {PERIOD}
- **Recipients**: Preparation responsible person
- **Trigger**: Status changes to "in_progress"
- **Content**:
  - Friendly reminder with task details
  - Progress bar
  - Your deadline
  - Direct link to task in Odoo

## Setting Up Automation Rules

Navigate to: **Settings → Technical → Automation → Create**

### Rule 1: 7-Day Warning Alert

```yaml
Name: BIR Deadline - 7 Days Warning
Model: BIR Filing Schedule (ipai.finance.bir_schedule)
Active: ✅ True

Trigger:
  Type: Based on Timed Condition
  Trigger Date: Filing Deadline
  Delay After Trigger Date: -7 days

Filter Domain:
  [
    ("status", "in", ["not_started", "in_progress"])
  ]

Actions to Do:
  Action: Send Email
  Email Template: BIR Deadline - 7 Days Warning
```

**Setup Steps**:
1. Click **Create**
2. **Name**: `BIR Deadline - 7 Days Warning`
3. **Model**: Select `BIR Filing Schedule`
4. **Trigger**: `Based on Timed Condition`
5. **Trigger Date**: Select `Filing Deadline`
6. **Delay After Trigger Date**: `-7` (Days)
7. **Apply on**: `Specified records`
8. **Domain**: `[("status", "in", ["not_started", "in_progress"])]`
9. **Action To Do**: `Send Email`
10. **Email Template**: Select `BIR Deadline - 7 Days Warning`
11. Click **Save**

### Rule 2: Overdue Alert

```yaml
Name: BIR Deadline - Overdue
Model: BIR Filing Schedule (ipai.finance.bir_schedule)
Active: ✅ True

Trigger:
  Type: Based on Timed Condition
  Trigger Date: Filing Deadline
  Delay After Trigger Date: 1 day

Filter Domain:
  [
    ("status", "!=", "filed")
  ]

Actions to Do:
  Action: Send Email
  Email Template: BIR Deadline - Overdue
```

**Setup Steps**:
1. Click **Create**
2. **Name**: `BIR Deadline - Overdue`
3. **Model**: Select `BIR Filing Schedule`
4. **Trigger**: `Based on Timed Condition`
5. **Trigger Date**: Select `Filing Deadline`
6. **Delay After Trigger Date**: `1` (Days)
7. **Apply on**: `Specified records`
8. **Domain**: `[("status", "!=", "filed")]`
9. **Action To Do**: `Send Email`
10. **Email Template**: Select `BIR Deadline - Overdue`
11. Click **Save**

### Rule 3: Task Completion Reminder

```yaml
Name: BIR Task - Completion Reminder
Model: BIR Filing Schedule (ipai.finance.bir_schedule)
Active: ✅ True

Trigger:
  Type: On Update
  Watch Fields: status

Filter Domain:
  [
    ("status", "=", "in_progress")
  ]

Actions to Do:
  Action: Send Email
  Email Template: BIR Task - Completion Reminder
```

**Setup Steps**:
1. Click **Create**
2. **Name**: `BIR Task - Completion Reminder`
3. **Model**: Select `BIR Filing Schedule`
4. **Trigger**: `On Update`
5. **Watch Fields**: Add `status`
6. **Apply on**: `Specified records`
7. **Domain**: `[("status", "=", "in_progress")]`
8. **Action To Do**: `Send Email`
9. **Email Template**: Select `BIR Task - Completion Reminder`
10. Click **Save**

## Setting Up Activity Reminders

Navigate to: **Settings → Technical → Automation → Create**

### Rule 4: Create Activity for Review Tasks

```yaml
Name: BIR Review - Create Activity
Model: BIR Filing Schedule (ipai.finance.bir_schedule)
Active: ✅ True

Trigger:
  Type: Based on Timed Condition
  Trigger Date: Review Deadline
  Delay After Trigger Date: -1 day

Filter Domain:
  [
    ("status", "=", "in_progress"),
    ("completion_pct", "<", 50)
  ]

Actions to Do:
  Action: Create Next Activity
  Activity Type: To-Do
  Summary: Review BIR Form: {{ object.form_code }} {{ object.period }}
  Responsible: Review Responsible Person
  Due Date Type: Days after trigger date
  Number of days: 1
```

**Setup Steps**:
1. Click **Create**
2. **Name**: `BIR Review - Create Activity`
3. **Model**: Select `BIR Filing Schedule`
4. **Trigger**: `Based on Timed Condition`
5. **Trigger Date**: Select `Review Deadline`
6. **Delay After Trigger Date**: `-1` (Days)
7. **Apply on**: `Specified records`
8. **Domain**: `[("status", "=", "in_progress"), ("completion_pct", "<", 50)]`
9. **Action To Do**: `Create Next Activity`
10. **Activity Type**: `To-Do`
11. **Summary**: `Review BIR Form: {{ object.form_code }} {{ object.period }}`
12. **Assigned to**: `Review Responsible Person` (field: `responsible_review`)
13. Click **Save**

## Testing Automation Rules

### Manual Test - 7-Day Warning

1. Navigate to: **Finance PPM → BIR Schedule → Create**
2. Fill in:
   - **BIR Form**: 1601-C
   - **Period**: Test December 2025
   - **BIR Filing Deadline**: (Today + 7 days)
   - **Responsible (Prep)**: Your test user
   - **Responsible (Review)**: Another test user
3. Click **Save**
4. Navigate to: **Settings → Technical → Automation**
5. Find: `BIR Deadline - 7 Days Warning`
6. Click **Run Manually**
7. Check your email inbox (both prep and review users)

### Manual Test - Overdue Alert

1. Navigate to: **Finance PPM → BIR Schedule → Create**
2. Fill in:
   - **BIR Form**: 2550Q
   - **Period**: Test Q3 2025
   - **BIR Filing Deadline**: (Yesterday)
   - **Status**: In Progress
   - **Responsible (Approval)**: Your test user
3. Click **Save**
4. Navigate to: **Settings → Technical → Automation**
5. Find: `BIR Deadline - Overdue`
6. Click **Run Manually**
7. Check your email inbox

### Manual Test - Task Reminder

1. Navigate to: **Finance PPM → BIR Schedule**
2. Open any existing BIR form
3. Change **Status** from "Not Started" to "In Progress"
4. Click **Save**
5. Check email inbox for preparation responsible person

## Troubleshooting

### Emails Not Sending

**Check 1: Outgoing Email Server**
- Navigate to: **Settings → Technical → Outgoing Mail Servers**
- Verify SMTP server configured correctly
- Test connection: Click **Test Connection**

**Check 2: Email Template**
- Navigate to: **Settings → Technical → Email Templates**
- Find template (e.g., `BIR Deadline - 7 Days Warning`)
- Click **Edit**
- Verify `email_to` field is correct
- Test: Click **Send Email** button

**Check 3: Automation Rule Active**
- Navigate to: **Settings → Technical → Automation**
- Verify rule is **Active** (checkbox ticked)
- Check **Trigger Date** field is set correctly
- Check **Filter Domain** matches your test data

**Check 4: Scheduled Actions**
- Navigate to: **Settings → Technical → Scheduled Actions**
- Find: `Mail: Email Queue Manager`
- Verify **Active** and **Next Execution Date** is set
- Manually run: Click **Run Manually**

### Automation Rule Not Triggering

**Check 1: Trigger Type**
- For time-based triggers: Verify **Trigger Date** field exists on model
- For update triggers: Verify **Watch Fields** are correct

**Check 2: Domain Filter**
- Navigate to: Automation rule
- Check **Apply on** is set to `Specified records`
- Verify **Domain** syntax: `[("field", "operator", "value")]`
- Test domain: Navigate to BIR Schedule → Filters → Add Custom Filter → Use same domain

**Check 3: Cron Job**
- Navigate to: **Settings → Technical → Scheduled Actions**
- Find: `Base Automation: Check to execute`
- Verify **Active** and runs regularly (every few minutes)
- Manually trigger: Click **Run Manually**

### Wrong Recipients

**Check Email Template**:
1. Navigate to: **Settings → Technical → Email Templates**
2. Find template
3. Check **Email To** field: `${object.responsible_prep.email}`
4. Verify field name matches model:
   - Prep: `responsible_prep`
   - Review: `responsible_review`
   - Approval: `responsible_approval`

**Check BIR Form**:
1. Navigate to: **Finance PPM → BIR Schedule**
2. Open BIR form
3. Verify all **Responsible** fields are filled
4. Check email addresses on user records

## Advanced Configurations

### Daily Digest Email

Create single daily email with all upcoming BIR deadlines:

1. Create Python Server Action:
   - **Model**: BIR Filing Schedule
   - **Code**:
     ```python
     # Fetch upcoming BIR forms (next 30 days)
     upcoming = env['ipai.finance.bir_schedule'].search([
         ('filing_deadline', '>=', fields.Date.today()),
         ('filing_deadline', '<=', fields.Date.today() + timedelta(days=30)),
         ('status', 'in', ['not_started', 'in_progress'])
     ], order='filing_deadline asc')

     # Send digest email
     if upcoming:
         template = env.ref('ipai_finance_ppm.email_template_bir_daily_digest')
         template.with_context(bir_forms=upcoming).send_mail(env.user.id)
     ```

2. Create Scheduled Action:
   - **Name**: BIR Daily Digest
   - **Model**: BIR Filing Schedule
   - **Execute**: Python Code (above)
   - **Interval**: 1 day
   - **Next Execution**: Tomorrow 8:00 AM

### Escalation Workflow

Auto-escalate to Finance Director if tasks not completed 3 days before deadline:

1. Create Automation Rule:
   - **Name**: BIR Escalation - 3 Days Before Deadline
   - **Model**: BIR Filing Schedule
   - **Trigger**: Based on Timed Condition
   - **Trigger Date**: Filing Deadline
   - **Delay**: -3 days
   - **Domain**: `[("completion_pct", "<", 80)]`
   - **Action**: Send Email to Approval Responsible Person

### Mattermost Integration

Send alerts to Mattermost channel instead of email:

1. Create Server Action with Python code:
   ```python
   import requests
   webhook_url = "https://mattermost.insightpulseai.net/hooks/xxx"
   payload = {
       "text": f"🚨 BIR Alert: {object.form_code} {object.period} due in 7 days",
       "username": "Finance PPM Bot"
   }
   requests.post(webhook_url, json=payload)
   ```

2. Add to Automation Rule as additional action

## Best Practices

✅ **Test First**: Always test automation rules with dummy data before enabling
✅ **Monitor Logs**: Check **Settings → Technical → Logging** for automation errors
✅ **Incremental Rollout**: Enable rules one at a time
✅ **Document Changes**: Keep record of custom automation rules
✅ **Regular Reviews**: Review automation effectiveness monthly
✅ **User Training**: Train responsible persons on how alerts work

## Support

For automation issues:
- Check Odoo logs: `/var/log/odoo/odoo.log`
- Test email server: Settings → Technical → Outgoing Mail Servers → Test Connection
- Verify cron jobs active: Settings → Technical → Scheduled Actions

## References

- Odoo Automation Documentation: https://www.odoo.com/documentation/18.0/applications/sales/subscriptions/automatic_alerts.html
- Email Templates: https://www.odoo.com/documentation/18.0/developer/reference/backend/data.html#mail-templates
- Scheduled Actions: https://www.odoo.com/documentation/18.0/developer/reference/backend/actions.html
