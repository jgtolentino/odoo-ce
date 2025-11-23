# PRD 003: Vibe Studio – AI-Driven Odoo Customization Engine

**Status:** Draft v0.1
**Created:** 2025-11-23
**Owner:** InsightPulseAI / Odoo CE Platform
**Repo:** `odoo-ce`
**Related:** `docs/VIBE_CODING_GUIDE.md`, `agents/odoo_reverse_mapper.yaml`

---

## 1. Problem Statement

### 1.1 Background

Odoo Studio is a powerful no-code/low-code tool that allows users to:
- Add custom fields to models
- Modify views (forms, lists, kanban)
- Create automation rules and webhooks
- Design PDF reports
- Configure approval workflows

**However:**
- Studio is **not available** in Odoo Community Edition
- Studio licenses require Odoo Online/Enterprise subscriptions
- Studio changes are stored in database, not versioned in Git
- Studio can trigger upsells and pricing changes

### 1.2 Our Approach

**Vibe Studio** = "Odoo Studio capabilities, but implemented as AI-generated code":

Instead of drag-and-drop UI, users:
1. Describe desired customization in **natural language**
2. AI generates **OCA-compliant module code**
3. Changes are **version-controlled**, **tested**, and **deployed** via standard Git workflow
4. Fully compatible with **Odoo CE** (no Enterprise required)

---

## 2. Goals & Non-Goals

### 2.1 Goals

**Primary:**
- ✅ Enable **Studio-like customization** (fields, views, automation) without Enterprise
- ✅ Generate **clean OCA-style modules** via AI vibe coding
- ✅ Track customization requests as structured records in Odoo
- ✅ Full **Git version control** + **CI/CD** for all customizations
- ✅ Integrate with `odoo_reverse_mapper` agent for automation

**Secondary:**
- ✅ Support **approval workflow** for customization requests
- ✅ Link generated modules to original business requests
- ✅ Provide **templates** for common customization patterns
- ✅ Enable **incremental module updates** (not full rewrites)

### 2.2 Non-Goals

- ❌ Build a drag-and-drop UI inside Odoo (too complex for MVP)
- ❌ Support live editing in production (all changes via Git)
- ❌ Replicate 100% of Studio features (focus on top 80%)
- ❌ Support Enterprise-only models or features

---

## 3. User Personas

### 3.1 Finance Manager (Requester)

**Needs:**
- Add custom fields to `project.task` for monthly closing tracking
- Create approval workflow for high-value expenses
- Generate custom PDF report for BIR submissions

**Pain Points:**
- Can't modify Odoo without developer help
- Odoo Studio not available on CE deployment
- Long wait times for custom development

**Vibe Studio Solution:**
- Create **Customization Request** in Odoo UI
- Describe need in plain language
- Developer/agent converts to vibe-coded module
- Changes deployed within hours, not days

---

### 3.2 Developer (Implementer)

**Needs:**
- Fast scaffolding of common customization patterns
- Clean, maintainable code (not Studio's database blobs)
- Version control and rollback capability
- Automated testing and CI validation

**Pain Points:**
- Repetitive boilerplate for simple customizations
- Manual module creation is slow
- Testing custom fields/views is tedious

**Vibe Studio Solution:**
- Read **Customization Request** from Odoo
- Use **vibe coding prompts** to generate module
- AI handles boilerplate, tests, security
- Deploy via standard Git workflow

---

### 3.3 Platform Architect (Approver)

**Needs:**
- Ensure all customizations follow CE/OCA standards
- Prevent Enterprise dependencies
- Maintain clean module architecture
- Track technical debt

**Pain Points:**
- Studio creates hidden database customizations
- Hard to audit or migrate Studio changes
- No clear dependency tracking

**Vibe Studio Solution:**
- All changes as **Git-tracked modules**
- **CI/CD validation** enforces CE/OCA compliance
- **Customization Request** provides audit trail
- Easy rollback via Git revert

---

## 4. High-Level Design

### 4.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Odoo CE (ERP)                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Module: ipai_vibe_studio                                  │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │  Model: ipai.vibe.request                            │ │ │
│  │  │  - target_model (Char)                               │ │ │
│  │  │  - customization_type (Selection: field/view/auto)   │ │ │
│  │  │  - description (Text)                                │ │ │
│  │  │  - state (draft/approved/generated/deployed/done)    │ │ │
│  │  │  - generated_module (Char)                           │ │ │
│  │  │  - branch_name (Char)                                │ │ │
│  │  │  - github_pr_url (Char)                              │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │ Webhook
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    n8n Workflow (Automation Hub)                 │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Workflow: W005_OD_VIBE_STUDIO_PROCESSOR                  │ │
│  │  1. Trigger: Odoo webhook (vibe.request state=approved)   │ │
│  │  2. Parse request → generate vibe prompt                  │ │
│  │  3. Call Claude Code CLI (via SSH/API)                    │ │
│  │  4. AI generates module code                              │ │
│  │  5. Create Git branch + commit                            │ │
│  │  6. Open GitHub PR                                        │ │
│  │  7. Update vibe.request (state=generated, pr_url=...)     │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │ SSH/API
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Claude Code CLI (Agent)                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Input: Vibe prompt from n8n                              │ │
│  │  Context: agents/ORCHESTRATOR.md, VIBE_CODING_GUIDE.md   │ │
│  │  Skills: scaffold_odoo_module, generate_views, write_tests│ │
│  │  Output: Full module under addons/ipai_vibe_<request_id>/ │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │ Git push
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   GitHub (Version Control)                       │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Branch: feature/vibe-studio-request-123                  │ │
│  │  Files:                                                    │ │
│  │    - addons/ipai_vibe_close_fields/__manifest__.py        │ │
│  │    - addons/ipai_vibe_close_fields/models/task.py         │ │
│  │    - addons/ipai_vibe_close_fields/views/task_views.xml   │ │
│  │    - addons/ipai_vibe_close_fields/security/...           │ │
│  │  PR: "Add monthly closing fields to project.task"         │ │
│  │  CI Checks: CE/OCA compliance, tests, security            │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────────┘
                         │ Merge → Deploy
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Production Odoo Server                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Module installed: ipai_vibe_close_fields                 │ │
│  │  project.task now has:                                    │ │
│  │    - x_close_stage_code                                   │ │
│  │    - x_finance_owner                                      │ │
│  │    - x_is_month_end_critical                              │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Core Components

#### Component 1: `ipai_vibe_studio` Module

**Models:**
- `ipai.vibe.request` (main customization request)
- `ipai.vibe.template` (reusable customization templates)
- `ipai.vibe.artifact` (link to generated modules/PRs)

**Views:**
- Customization request form (user-friendly input)
- Request kanban board (draft → approved → generated → deployed)
- Template library (common patterns)

**Security:**
- `vibe_studio_user` (can create requests)
- `vibe_studio_manager` (can approve requests)
- `vibe_studio_developer` (can mark as deployed)

---

#### Component 2: n8n Workflow Processor

**Workflow:** `W005_OD_VIBE_STUDIO_PROCESSOR.json`

**Nodes:**
1. **Webhook Trigger** (Odoo → n8n when request approved)
2. **Parse Request** (extract target_model, type, description)
3. **Generate Vibe Prompt** (use template from VIBE_CODING_GUIDE.md)
4. **Execute Claude Code CLI** (SSH to dev server, run vibe coding)
5. **Git Operations** (create branch, commit, push)
6. **Create GitHub PR** (via `gh pr create`)
7. **Update Odoo** (set state=generated, pr_url, module_name)
8. **Notify Requester** (email/Mattermost)

**Error Handling:**
- Retry SSH/Git operations 3x
- If AI generation fails → set state=failed, notify developer
- Log all steps to n8n execution history

---

#### Component 3: Claude Code CLI Agent

**Operating Mode:**
- Runs on dev server or GitHub Actions runner
- Receives vibe prompt from n8n
- Uses `agents/ORCHESTRATOR.md` + `docs/VIBE_CODING_GUIDE.md`
- Generates module following OCA standards
- Runs basic validation (manifest syntax, import checks)

**Skills Used:**
- `scaffold_odoo_module`
- `generate_model_fields`
- `generate_views`
- `write_security_rules`
- `write_tests`

---

## 5. Functional Requirements

### 5.1 Customization Request Workflow

**User Story:**
> As a Finance Manager, I want to add custom fields to project.task for monthly closing tracking, so I can monitor close status in Odoo without spreadsheets.

**Steps:**

1. **Create Request:**
   - Navigate: Vibe Studio → Customization Requests → Create
   - Fill form:
     - **Target Model:** `project.task`
     - **Type:** Add Fields
     - **Description:**
       ```
       Add these fields to project.task:
       - x_close_stage_code (Char, required)
       - x_finance_owner (Many2one res.users)
       - x_is_month_end_critical (Boolean, default False)

       Show fields in:
       - Task form (editable)
       - Task tree (read-only)
       - Task kanban (badge for critical tasks)
       ```
   - Save → State: `draft`

2. **Approval:**
   - Architect reviews request
   - Checks: no Enterprise deps, clear requirements
   - Click **Approve** → State: `approved`
   - Triggers n8n webhook

3. **Generation:**
   - n8n receives webhook
   - Generates vibe prompt
   - Calls Claude Code CLI
   - AI generates module: `ipai_vibe_close_fields`
   - Creates Git branch: `feature/vibe-studio-request-123`
   - Opens PR
   - Updates request → State: `generated`, PR URL populated

4. **Review & Deploy:**
   - Developer reviews PR
   - CI validates: CE/OCA compliance, tests pass
   - Merge PR
   - Deploy script runs
   - Developer marks request → State: `deployed`

5. **Validation:**
   - Finance manager opens project.task form
   - Sees new fields
   - Marks request → State: `done`

---

### 5.2 Supported Customization Types

#### Type 1: Add Fields

**Input:**
- Target model (e.g., `project.task`, `account.move`)
- Field definitions (name, type, widget, required, help)
- View placements (form, tree, search, kanban)

**Output:**
- Module with model inheritance
- View inheritance snippets
- Security rules for new fields

**Example Module:** `ipai_vibe_close_fields`

---

#### Type 2: Modify Views

**Input:**
- Target view (e.g., project.task form)
- Changes (add notebook page, reorder fields, add domain filter)

**Output:**
- View inheritance with XPath
- Updated arch structure

**Example Module:** `ipai_vibe_task_layout`

---

#### Type 3: Automation Rules

**Input:**
- Trigger (record create/update, field change)
- Conditions (domain filter)
- Action (send email, update field, create activity)

**Output:**
- `ir.actions.server` records
- Python methods in models (if complex logic)
- Tests for automation trigger

**Example Module:** `ipai_vibe_expense_alerts`

---

#### Type 4: PDF Reports

**Input:**
- Report name and purpose
- Data to include (which fields)
- Layout (header, footer, sections)

**Output:**
- QWeb template
- Report action
- Print button on form

**Example Module:** `ipai_vibe_bir_report`

---

#### Type 5: Approval Workflows

**Input:**
- Model to add approval to
- Approval stages (draft → review → approve → done)
- Approver groups
- Notification logic

**Output:**
- State field + transitions
- Groups and record rules
- Email templates
- Activity creation on state change

**Example Module:** `ipai_vibe_expense_approval`

---

### 5.3 Customization Templates

**Pre-built templates for common patterns:**

| Template ID | Name | Description | Fields Required |
|------------|------|-------------|-----------------|
| `tpl_add_fields_simple` | Add Simple Fields | Add 1-5 basic fields to existing model | target_model, field_list |
| `tpl_add_fields_relational` | Add Relational Fields | Add Many2one/Many2many fields | target_model, field_defs, related_models |
| `tpl_add_notebook_page` | Add Notebook Page | Add new tab to form view | target_model, page_name, fields |
| `tpl_state_workflow` | State Workflow | Add state field + transitions | target_model, states, transitions |
| `tpl_cron_job` | Scheduled Action | Add cron job | cron_name, interval, python_code |
| `tpl_webhook_endpoint` | Webhook Endpoint | Add controller for n8n/external calls | endpoint_path, auth_method, payload_schema |

**Usage:**
1. Select template
2. Fill template-specific fields
3. Generate → AI uses template as base, customizes per request

---

## 6. Technical Specifications

### 6.1 Data Model

#### Model: `ipai.vibe.request`

```python
class VibeStudioRequest(models.Model):
    _name = 'ipai.vibe.request'
    _description = 'Vibe Studio Customization Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'priority desc, create_date desc'

    name = fields.Char(required=True, tracking=True)
    description = fields.Html(required=True)
    target_model = fields.Char(required=True, help="e.g., project.task, account.move")
    customization_type = fields.Selection([
        ('fields', 'Add/Modify Fields'),
        ('views', 'Modify Views'),
        ('automation', 'Automation Rules'),
        ('reports', 'PDF Reports'),
        ('approval', 'Approval Workflow'),
        ('other', 'Other'),
    ], required=True, default='fields')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('generating', 'Generating'),
        ('generated', 'Generated'),
        ('testing', 'Testing'),
        ('deployed', 'Deployed'),
        ('done', 'Done'),
        ('rejected', 'Rejected'),
        ('failed', 'Failed'),
    ], default='draft', tracking=True)

    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High'),
        ('3', 'Critical'),
    ], default='1')

    requester_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    approver_id = fields.Many2one('res.users')
    developer_id = fields.Many2one('res.users')

    # Generation outputs
    generated_module = fields.Char(help="Module name, e.g., ipai_vibe_close_fields")
    branch_name = fields.Char(help="Git branch name")
    github_pr_url = fields.Char(string="GitHub PR")
    vibe_prompt = fields.Text(help="AI prompt used for generation")

    # Links
    artifact_ids = fields.One2many('ipai.vibe.artifact', 'request_id')

    # Template
    template_id = fields.Many2one('ipai.vibe.template')

    # Metadata
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    def action_submit_for_approval(self):
        self.write({'state': 'pending_approval'})
        # Send email/activity to approver

    def action_approve(self):
        self.write({
            'state': 'approved',
            'approver_id': self.env.user.id,
        })
        # Trigger webhook to n8n
        self._trigger_generation_workflow()

    def action_reject(self):
        self.write({'state': 'rejected'})

    def _trigger_generation_workflow(self):
        """Send webhook to n8n to start generation"""
        # POST to n8n webhook with request data
        pass
```

---

#### Model: `ipai.vibe.template`

```python
class VibeStudioTemplate(models.Model):
    _name = 'ipai.vibe.template'
    _description = 'Vibe Studio Customization Template'

    name = fields.Char(required=True)
    code = fields.Char(required=True, help="e.g., tpl_add_fields_simple")
    description = fields.Text()
    customization_type = fields.Selection([...], required=True)

    vibe_prompt_template = fields.Text(
        help="Jinja2 template for generating vibe prompt"
    )

    # Fields that template requires
    required_fields = fields.Text(help="JSON schema of required inputs")

    example_output = fields.Text(help="Example module structure")
```

---

#### Model: `ipai.vibe.artifact`

```python
class VibeStudioArtifact(models.Model):
    _name = 'ipai.vibe.artifact'
    _description = 'Vibe Studio Generated Artifacts'

    request_id = fields.Many2one('ipai.vibe.request', required=True, ondelete='cascade')
    artifact_type = fields.Selection([
        ('module', 'Odoo Module'),
        ('pr', 'GitHub PR'),
        ('test_result', 'Test Results'),
        ('doc', 'Documentation'),
    ], required=True)

    path = fields.Char(help="Path in repo or URL")
    ref = fields.Char(help="Git commit SHA or PR number")
    notes = fields.Text()
```

---

### 6.2 n8n Workflow Schema

**File:** `notion-n8n-monthly-close/workflows/W005_OD_VIBE_STUDIO_PROCESSOR.json`

**Nodes:**

```json
{
  "nodes": [
    {
      "id": "webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "vibe-studio-request",
        "method": "POST"
      }
    },
    {
      "id": "parse_request",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Extract vibe request fields\nconst request = items[0].json;\nreturn [{\n  json: {\n    request_id: request.id,\n    target_model: request.target_model,\n    customization_type: request.customization_type,\n    description: request.description,\n    requester: request.requester_id\n  }\n}];"
      }
    },
    {
      "id": "generate_vibe_prompt",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Use template from VIBE_CODING_GUIDE.md\nconst { target_model, customization_type, description } = items[0].json;\nconst prompt = `\nGoal:\n  ${description}\n\nTarget: ${target_model}\nType: ${customization_type}\n\nConstraints:\n  - Odoo 18 CE only\n  - Follow OCA conventions\n  - Place under addons/ipai_vibe_${request_id}/\n\nDeliverables:\n  - Full module structure\n  - Tests\n  - Security rules\n`;\nreturn [{ json: { vibe_prompt: prompt } }];"
      }
    },
    {
      "id": "execute_claude_cli",
      "type": "n8n-nodes-base.ssh",
      "parameters": {
        "host": "dev.insightpulseai.net",
        "command": "cd /home/user/odoo-ce && claude --prompt \"$VIBE_PROMPT\""
      }
    },
    {
      "id": "git_commit_push",
      "type": "n8n-nodes-base.ssh",
      "parameters": {
        "command": "cd /home/user/odoo-ce && git checkout -b feature/vibe-studio-request-${request_id} && git add addons/ipai_vibe_* && git commit -m 'feat(vibe): ${description}' && git push -u origin HEAD"
      }
    },
    {
      "id": "create_github_pr",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "https://api.github.com/repos/jgtolentino/odoo-ce/pulls",
        "authentication": "headerAuth",
        "body": {
          "title": "Vibe Studio: ${description}",
          "head": "feature/vibe-studio-request-${request_id}",
          "base": "main"
        }
      }
    },
    {
      "id": "update_odoo_request",
      "type": "n8n-nodes-base.odoo",
      "parameters": {
        "operation": "update",
        "model": "ipai.vibe.request",
        "id": "${request_id}",
        "fieldsToUpdate": {
          "state": "generated",
          "github_pr_url": "${pr_url}",
          "branch_name": "feature/vibe-studio-request-${request_id}"
        }
      }
    },
    {
      "id": "notify_requester",
      "type": "n8n-nodes-base.emailSend",
      "parameters": {
        "to": "${requester_email}",
        "subject": "Vibe Studio: Your customization is ready for review",
        "text": "PR: ${pr_url}"
      }
    }
  ]
}
```

---

### 6.3 Vibe Prompt Generation Logic

**Input:** `ipai.vibe.request` record

**Output:** Structured vibe prompt

**Template (Jinja2):**

```jinja2
You are building Odoo 18 CE modules in the odoo-ce repo.

Goal:
  {{ request.description }}

Target Model: {{ request.target_model }}
Customization Type: {{ request.customization_type }}

Constraints:
  - Odoo 18 CE only (no Enterprise)
  - Follow OCA development guidelines
  - Module name: ipai_vibe_{{ request.id }}
  - Place under addons/ipai_vibe_{{ request.id }}/
  - Multi-company aware
  - AGPL-3 license

{% if request.template_id %}
Reference Template:
{{ request.template_id.vibe_prompt_template }}
{% endif %}

Deliverables:
  1. Complete module structure:
     - __manifest__.py
     - models/*.py
     - views/*.xml
     - security/ir.model.access.csv
     - tests/test_*.py
  2. README.rst explaining:
     - Purpose
     - Installation
     - Usage
  3. Tests validating:
     - New fields/views work
     - Security rules correct
     - No regressions

Do NOT:
  - Add Enterprise imports
  - Skip tests
  - Create external React apps

Step-by-step:
  1. Inspect target model: {{ request.target_model }}
  2. Propose file tree
  3. Generate implementation
  4. Provide install command
```

---

## 7. Implementation Plan

### Phase 1: Foundation (Week 1-2)

**Deliverables:**
- [ ] Module `ipai_vibe_studio` scaffolded
- [ ] Models: `ipai.vibe.request`, `ipai.vibe.template`, `ipai.vibe.artifact`
- [ ] Views: request form, kanban, list
- [ ] Security: groups and access rules
- [ ] Demo data: 3 sample templates

**Acceptance Criteria:**
- Users can create, submit, approve requests
- Requests tracked through states
- Templates library available

---

### Phase 2: n8n Integration (Week 3)

**Deliverables:**
- [ ] n8n workflow: `W005_OD_VIBE_STUDIO_PROCESSOR`
- [ ] Webhook: Odoo → n8n on request approval
- [ ] Vibe prompt generation from template
- [ ] SSH execution to dev server

**Acceptance Criteria:**
- Webhook fires on approval
- n8n receives request data
- Vibe prompt generated correctly

---

### Phase 3: AI Generation (Week 4)

**Deliverables:**
- [ ] Claude Code CLI integration
- [ ] Git branch creation + commit
- [ ] GitHub PR creation via `gh` CLI
- [ ] Update Odoo request with PR URL

**Acceptance Criteria:**
- AI generates valid Odoo module
- Module passes basic syntax checks
- PR created successfully
- Request state updated to `generated`

---

### Phase 4: Testing & Validation (Week 5)

**Deliverables:**
- [ ] CI/CD workflow for generated modules
- [ ] CE/OCA compliance checks
- [ ] Test execution in CI
- [ ] Deployment script integration

**Acceptance Criteria:**
- Generated modules pass CI
- No Enterprise dependencies
- Tests execute and pass
- Modules deployable to production

---

### Phase 5: Templates & Polish (Week 6)

**Deliverables:**
- [ ] 5+ reusable templates
- [ ] Template usage documentation
- [ ] Request form improvements (template selector)
- [ ] Error handling and retry logic

**Acceptance Criteria:**
- Users can select templates
- Templates reduce required input
- Error messages clear and actionable
- Retry logic handles transient failures

---

## 8. Success Criteria

**MVP Success (After Phase 5):**

- ✅ 10+ customization requests processed successfully
- ✅ 80%+ AI-generated modules pass CI without manual fixes
- ✅ Average time from request → deployed: < 4 hours
- ✅ 0 Enterprise dependencies introduced
- ✅ 5+ templates covering common patterns
- ✅ Finance team can self-serve simple field additions

**Long-Term Success (6 months):**

- ✅ 50+ customizations deployed
- ✅ 90%+ success rate for template-based requests
- ✅ Average time from request → deployed: < 2 hours
- ✅ 20+ templates covering 80% of use cases
- ✅ Vibe Studio becomes primary customization method (over manual dev)

---

## 9. Risks & Mitigations

### Risk 1: AI Generates Invalid Code

**Likelihood:** Medium
**Impact:** High

**Mitigation:**
- CI/CD validation before merge
- Template-based prompts (reduce variability)
- Developer review required for all PRs
- Rollback via Git revert if issues found

---

### Risk 2: Security Vulnerabilities

**Likelihood:** Low
**Impact:** Critical

**Mitigation:**
- Security rules required in all generated modules
- CI checks for: SQL injection, XSS, unsafe `eval()`
- RLS validation for Supabase integrations
- Code review by platform architect

---

### Risk 3: Technical Debt Accumulation

**Likelihood:** Medium
**Impact:** Medium

**Mitigation:**
- Module naming convention: `ipai_vibe_<request_id>`
- Regular refactoring sprints (consolidate related modules)
- Deprecation policy for unused modules
- Track module dependencies in `MODULE_SERVICE_MATRIX.md`

---

### Risk 4: Template Maintenance Burden

**Likelihood:** Low
**Impact:** Low

**Mitigation:**
- Start with 5 high-value templates
- Add new templates only when pattern repeats 3+ times
- Version templates (allow updates without breaking old requests)

---

## 10. Open Questions

1. **Should vibe-generated modules be permanent or temporary?**
   - **Option A:** Keep as permanent modules (easier to track)
   - **Option B:** Consolidate into larger modules after validation (cleaner architecture)
   - **Recommendation:** Option A for MVP, Option B for long-term

2. **How to handle module updates (not just creation)?**
   - **Option A:** New request creates new version (ipai_vibe_123_v2)
   - **Option B:** Update existing module (incremental changes)
   - **Recommendation:** Option B (AI uses Read + Edit tools, not just Write)

3. **Should templates be stored in DB or Git?**
   - **Option A:** DB (easier UI management)
   - **Option B:** Git (version controlled, code review)
   - **Recommendation:** Option B (Git), with UI for selection

4. **Who can deploy generated modules to production?**
   - **Option A:** Automatic after CI passes
   - **Option B:** Manual approval required
   - **Recommendation:** Option B for MVP (safety), Option A for mature templates

---

## 11. References

- **Vibe Coding Methodology:** `docs/VIBE_CODING_GUIDE.md`
- **Agent Framework:** `agents/ORCHESTRATOR.md`, `agents/odoo_reverse_mapper.yaml`
- **Odoo Studio Docs:** https://www.odoo.com/documentation/18.0/applications/studio.html
- **OCA Development Guidelines:** https://github.com/OCA/odoo-community.org
- **Module Examples:** `addons/ipai_expense/`, `addons/ipai_equipment/`

---

**Version:** 0.1 (Draft)
**Status:** Awaiting Approval
**Next Steps:** Build Phase 1 (Foundation)
**Target MVP Date:** 2025-12-21

---

🤖 **Vibe Studio: Making Odoo customization as easy as describing what you want.**
