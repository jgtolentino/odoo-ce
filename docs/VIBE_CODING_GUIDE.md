# Vibe Coding Guide for InsightPulse Odoo CE

**Status:** Active v1.0
**Created:** 2025-11-23
**Repo:** `odoo-ce` (InsightPulse ERP)
**Scope:** Odoo 18 CE + OCA modules, agent integrations, SaaS reverse engineering

---

## 🎯 What Is "Vibe Coding"?

**Vibe coding** is outcome-driven development where you describe the **business outcome and constraints**, not the line-by-line implementation. An AI assistant (Claude Code CLI, Copilot, etc.) handles:

- Stack selection and architecture decisions
- Code scaffolding and boilerplate
- Test generation and validation
- Iterative refinement based on failures

**In this repo, vibe coding powers:**
- 🔄 **SaaS Reverse Engineering** → Replicate Cheqroom, Concur, Clarity PPM as Odoo CE modules
- 🏗️ **Module Generation** → Scaffold `ipai_*` modules from outcome-focused prompts
- 🤖 **Agent Orchestration** → Autonomous execution via `odoo_reverse_mapper` agent
- 📊 **Feature Parity** → Systematic mapping of Enterprise features to CE/OCA alternatives

---

## 🔗 Integration with Agent Framework

This guide is part of the **InsightPulse Agent Skills Architecture**:

```
agents/
├── ORCHESTRATOR.md              ← Master agent operating system
├── odoo_reverse_mapper.yaml     ← SaaS → Odoo CE reverse engineering agent
├── AGENT_SKILLS_REGISTRY.yaml   ← 15+ atomic skills + capabilities
└── docs/VIBE_CODING_GUIDE.md    ← This file (methodology)
```

**How they work together:**
1. **Vibe Coding** = The methodology (how to prompt for outcomes)
2. **Orchestrator** = The agent operating system (how agents execute)
3. **Reverse Mapper** = The automation engine (autonomous SaaS reverse engineering)

---

## 📋 Core Principles

### 1. Outcome First, Implementation Second

**❌ Don't say:**
> "Create a Python class called EquipmentAsset that inherits from models.Model with fields for serial_number, condition, and location_id pointing to stock.location"

**✅ Do say:**
> "Implement Cheqroom-style equipment management: track physical assets with serial numbers, custody chain, check-out/return workflows, and overdue notifications. Must work inside Odoo CE project module with no Enterprise dependencies."

### 2. Respect CE/OCA Guardrails

**Always enforce:**
- ✅ Odoo Community Edition 18 only
- ✅ OCA-style modules (manifest, security, tests, demo)
- ✅ `ipai_` namespace for custom modules
- ✅ AGPL-3 license
- ❌ No Enterprise imports
- ❌ No IAP services
- ❌ No `odoo.com` upsell links

**Validation command:**
```bash
# Must return empty
grep -r "OEEL\|odoo.com" addons/ipai_*/  --exclude-dir=static
```

### 3. Use the Agent Framework

**Before vibe coding manually, check if agent can do it:**

| Task | Use Agent Capability |
|------|---------------------|
| Replicate SaaS feature | `odoo_reverse_mapper` + `run_clarity_ppm_reverse.sh` |
| Improve OCR quality | `cap_improve_ocr_quality` |
| Create n8n workflow | `cap_n8n_finance_automation` |
| Deploy module | `cap_odoo_supabase_module` |

**Agent invocation (via Claude Code CLI):**
```bash
cd /home/user/odoo-ce
claude

# In Claude session:
> Load agents/ORCHESTRATOR.md as your operating system.
> Execute the odoo_reverse_mapper capability for Clarity PPM.
> Map portfolio management features to Odoo CE and generate ipai_ppm_portfolio.
```

### 4. Tests, Then Code

**Always generate:**
- Unit tests (`tests/test_*.py`)
- Demo data (`demo/*.xml`)
- Access rules (`security/ir.model.access.csv`)
- Documentation (`README.rst`)

**Validation:**
```bash
python odoo-bin -d test_db -i ipai_equipment --test-enable --stop-after-init
```

### 5. Short Feedback Cycles

**Don't:**
- Ask for 10 modules at once
- Generate full implementation before testing

**Do:**
- Generate one module skeleton
- Install and run tests
- Feed errors back to AI
- Iterate until green

---

## 🚀 Vibe Coding Workflows

### Workflow 1: Manual Vibe Coding (One-Off Feature)

**When:** Building a single module/feature without full agent automation

**Steps:**

1. **Prepare branch:**
   ```bash
   git checkout -b claude/vibe-coding-ipai-equipment
   ```

2. **Give AI context:**
   - Point to: `README.md`, `spec.md`, `agents/ORCHESTRATOR.md`
   - Show existing modules: `addons/ipai_expense/`, `addons/ipai_docs/`

3. **Use outcome-driven prompt:**
   ```text
   Goal:
     Implement ipai_equipment module for Cheqroom-style equipment management.

   Constraints:
     - Odoo 18 CE only (no Enterprise)
     - Follow OCA conventions
     - Use ipai_ namespace
     - Multi-company aware (TBWA SMP, W9, InsightPulseAI)

   Deliverables:
     1. Complete module under addons/ipai_equipment/
     2. Models: equipment, booking, incident
     3. Views: tree, form, kanban, calendar
     4. Security: ir.model.access.csv + record rules
     5. Tests: booking overlap prevention, overdue detection
     6. Demo data: 5 sample equipments
   ```

4. **Feedback loop:**
   ```bash
   # Install
   python odoo-bin -d test_db -i ipai_equipment --stop-after-init

   # If errors, paste traceback back to AI:
   # "Got this error: psycopg2.errors.UndefinedTable..."
   ```

5. **Validate:**
   ```bash
   # Run tests
   python odoo-bin -d test_db -i ipai_equipment --test-enable

   # Check compliance
   grep -r "OEEL\|enterprise" addons/ipai_equipment/
   ```

---

### Workflow 2: Agent-Driven Vibe Coding (SaaS Parity)

**When:** Replicating entire SaaS products (Cheqroom, Concur, Clarity PPM)

**Steps:**

1. **Define SaaS product in Supabase:**
   ```sql
   INSERT INTO saas_products (slug, name, homepage_url, category)
   VALUES ('clarity_ppm', 'Clarity PPM', 'https://www.broadcom.com/...', 'ppm');
   ```

2. **Map features:**
   ```sql
   INSERT INTO saas_feature_mappings (
     saas_product_id, feature_key, feature_name,
     category, status, criticality
   )
   SELECT id, 'portfolio_hierarchy', 'Portfolio → Program → Project Hierarchy',
          'portfolio', 'gap', 5
   FROM saas_products WHERE slug = 'clarity_ppm';
   ```

3. **Trigger reverse mapping agent:**
   ```bash
   ./scripts/run_clarity_ppm_reverse.sh
   ```

   **What it does:**
   - Discovers features from Supabase
   - Maps to CE/OCA modules
   - Calculates coverage gap
   - Scaffolds `ipai_ppm_*` modules
   - Generates PRDs
   - Updates Supabase tracking
   - Creates GitHub issue

4. **Review generated artifacts:**
   ```bash
   ls -la addons/ipai_ppm_*/
   cat docs/PRD_ipai_ppm_portfolio.md
   ```

5. **Complete implementation:**
   ```bash
   # The agent scaffolds structure; you implement business logic
   cd addons/ipai_ppm_portfolio
   # Edit models, views, tests

   # Deploy
   ./scripts/deploy-odoo-modules.sh ipai_ppm_portfolio
   ```

---

### Workflow 3: Vibe Studio (Studio-Like Customization)

**When:** Users want Studio-like field/view/automation customization but in code

**See:** `specs/003-vibe-studio.prd.md` (coming soon)

**Concept:**
- Users describe customization intent in Odoo UI (`ipai.vibe.request` record)
- Developer/agent converts to vibe prompt
- AI generates module changes
- Validate → Deploy → Track

**Example request:**
```text
Target: project.task
Add fields:
  - x_close_stage_code (Char)
  - x_finance_owner (Many2one res.users)
  - x_is_month_end_critical (Boolean)
Expose in: task form, task tree (read-only)
Module: ipai_close_task_fields
```

---

## 📝 Prompt Templates

### Template 1: New Module from Scratch

```text
You are building Odoo 18 CE modules in the odoo-ce repo.

Goal:
  Create ipai_<MODULE_NAME> for <BUSINESS_OUTCOME>.

Context:
  - SaaS product being replaced: <PRODUCT>
  - Core features: <FEATURE_1>, <FEATURE_2>, <FEATURE_3>

Constraints:
  - Odoo 18 CE only (no Enterprise modules)
  - Follow OCA development guidelines
  - Use ipai_ namespace
  - Place under addons/ipai_<MODULE>/
  - Multi-company support required
  - Integration points:
    * OCR: ocr.insightpulseai.net/ocr/expense
    * n8n: ipa.insightpulseai.net/webhook/...
    * Supabase: tracked in saas_feature_mappings

Deliverables:
  1. Full module structure:
     - __manifest__.py (correct dependencies, AGPL-3)
     - models/*.py (with docstrings)
     - views/*.xml (form, tree, search, kanban)
     - security/ir.model.access.csv
     - data/*.xml (sequences, states, defaults)
     - demo/*.xml (5+ sample records)
     - tests/test_*.py (unit + integration)
  2. README.rst explaining:
     - Purpose and business value
     - User roles and permissions
     - Day-in-the-life workflow
     - Integration with monthly closing
  3. Tests that validate:
     - Model constraints
     - State transitions
     - Access rules
     - Multi-company isolation

Do NOT:
  - Generate Docker configs (separate repo)
  - Create React/Vue frontends (use Odoo's QWeb)
  - Add Enterprise imports
  - Skip tests or security rules

Step-by-step:
  1. Inspect existing ipai_* modules for patterns
  2. Propose file tree
  3. Generate complete implementation
  4. Provide installation command
```

---

### Template 2: Extend Existing Module

```text
Goal:
  Extend ipai_expense to support OCR receipt auto-linking.

Context:
  - Current: ipai_expense handles cash advances + expense reports
  - OCR service: ocr.insightpulseai.net (already deployed)
  - n8n workflow will trigger: webhook → OCR → Odoo

Requirements:
  - Add model: ipai.expense.ocr.log
    * Fields: expense_id, ocr_payload (JSON), status, vendor, total, date
  - Add button on expense form: "Attach OCR Receipt"
  - Add controller: /ipai/expense/ocr/process (for n8n)
  - Update security: ir.model.access.csv
  - Add tests: receipt linking, OCR total matching

Constraints:
  - Odoo 18 CE only
  - Keep changes within addons/ipai_expense/
  - No direct HTTP calls in models (use controller)
  - Follow existing ipai_expense patterns

Deliverables:
  - Updated models/
  - Updated views/ (new button + form)
  - New controllers/ocr.py
  - Updated security/
  - New tests/test_ocr.py
  - Migration notes in README.rst
```

---

### Template 3: n8n Workflow Generation

```text
Goal:
  Create n8n workflow for BIR tax deadline alerts.

Context:
  - BIR deadlines stored in: Odoo → ipai.tax.deadline model
  - Alert 7 days before: email CFO + post to Mattermost
  - Domain code: OD (Odoo)
  - Sequence: W002 (next available)

Requirements:
  - Workflow file: notion-n8n-monthly-close/workflows/W002_OD_BIR_ALERTS.json
  - Trigger: Schedule (daily 6am Manila time)
  - Nodes:
    1. Odoo JSON-RPC → fetch upcoming deadlines
    2. Filter → deadlines within 7 days
    3. Email → CFO
    4. Mattermost → #finance channel with @cfo mention
  - Error handling: retry 3x, notify on failure

Deliverables:
  - W002_OD_BIR_ALERTS.json (full n8n workflow)
  - Register in: workflows/index.yaml
  - Documentation: README snippet with:
    * Purpose
    * Trigger schedule
    * Example Mattermost message
    * Error handling
```

---

## 🔍 Quality Checklist

Before merging any vibe-coded module:

**Compliance:**
- [ ] No Enterprise modules referenced
- [ ] No `odoo.com` links in user-facing code
- [ ] AGPL-3 license in `__manifest__.py`
- [ ] Author: InsightPulseAI

**OCA Standards:**
- [ ] Manifest has: `name`, `version`, `category`, `author`, `license`, `depends`, `data`
- [ ] Models have docstrings
- [ ] Views have proper `arch` structure
- [ ] Security rules defined (groups + record rules)

**Testing:**
- [ ] Unit tests exist (`tests/test_*.py`)
- [ ] Tests pass: `python odoo-bin -d test_db -i <module> --test-enable`
- [ ] Demo data loads without errors

**Integration:**
- [ ] Module appears in Apps list
- [ ] Views render correctly
- [ ] No JS/CSS errors in browser console
- [ ] Multi-company aware (if applicable)

**Documentation:**
- [ ] README.rst exists
- [ ] Installation steps clear
- [ ] User workflow documented
- [ ] Integration points listed

---

## 🤖 Agent Framework Reference

### Key Files

| File | Purpose | When to Use |
|------|---------|-------------|
| `agents/ORCHESTRATOR.md` | Agent operating system | Every agent session start |
| `agents/odoo_reverse_mapper.yaml` | SaaS reverse engineering spec | Replicating SaaS products |
| `agents/AGENT_SKILLS_REGISTRY.yaml` | Available skills/capabilities | Finding the right capability |
| `scripts/run_clarity_ppm_reverse.sh` | Clarity PPM automation | Execute Clarity PPM parity |
| `docs/VIBE_CODING_GUIDE.md` | This file | Manual vibe coding |

### Capabilities Reference

| Capability ID | Use Case | Skills Used |
|---------------|----------|-------------|
| `cap_odoo_supabase_module` | New Odoo module + Supabase integration | scaffold → implement → test → deploy |
| `cap_improve_ocr_quality` | OCR accuracy improvement | analyze → normalize → test → monitor |
| `cap_n8n_finance_automation` | n8n workflow creation | create → register → deploy → validate |
| `cap_deploy_digitalocean` | Infrastructure deployment | provision → deploy → ssl → validate |
| `cheqroom_parity_equipment_ce` | Cheqroom equipment parity | Full ipai_equipment validation |
| `concur_parity_expense_ce` | Concur expense parity | Full ipai_expense + OCR validation |
| `workspace_parity_docs_projects_ce` | Notion workspace parity | Full ipai_docs validation |

---

## 🎯 Example: End-to-End Vibe Coding Session

### Scenario: Build ipai_equipment Module

**User Request:**
> "Create equipment management like Cheqroom inside Odoo CE"

**Agent Execution:**

1. **Load context:**
   ```bash
   cd /home/user/odoo-ce
   claude
   > Load agents/ORCHESTRATOR.md
   > Load docs/VIBE_CODING_GUIDE.md
   > Read agents/odoo_reverse_mapper.yaml
   ```

2. **Check if agent can automate:**
   ```
   > Check AGENT_SKILLS_REGISTRY.yaml for "equipment" capability
   > Found: cheqroom_parity_equipment_ce
   > Decision: Use semi-automated approach (manual PRD + agent scaffold)
   ```

3. **Generate PRD:**
   ```
   > Use Template 1: New Module from Scratch
   > Goal: ipai_equipment for Cheqroom parity
   > Generate: docs/PRD_ipai_equipment.md
   ```

4. **Scaffold module:**
   ```bash
   odoo-bin scaffold ipai_equipment addons
   ```

5. **Vibe code implementation:**
   ```
   > Implement models: equipment, booking, incident
   > Generate views: form, tree, calendar, kanban
   > Add security: equipment_user, equipment_manager groups
   > Write tests: test_booking_overlap, test_overdue_detection
   > Add demo: 5 sample equipments with bookings
   ```

6. **Validate:**
   ```bash
   # Install
   python odoo-bin -d test_cheqroom -i ipai_equipment --stop-after-init

   # Run tests
   python odoo-bin -d test_cheqroom -i ipai_equipment --test-enable

   # Check compliance
   grep -r "OEEL\|enterprise" addons/ipai_equipment/
   ```

7. **Deploy:**
   ```bash
   ./scripts/deploy-odoo-modules.sh ipai_equipment
   ```

8. **Track in Supabase:**
   ```sql
   UPDATE saas_feature_mappings
   SET status = 'covered', ipai_modules = ARRAY['ipai_equipment']
   WHERE saas_product_id = (SELECT id FROM saas_products WHERE slug = 'cheqroom');
   ```

9. **Document:**
   ```bash
   cat >> docs/FEATURE_CHEQROOM_PARITY.md
   ```

**Result:**
- ✅ Full ipai_equipment module deployed
- ✅ All tests passing
- ✅ Feature parity documented
- ✅ Supabase tracking updated
- ✅ Ready for UAT

---

## 🔧 Troubleshooting

### "AI Generated Enterprise Import"

**Symptom:**
```python
from odoo.addons.project_enterprise import ...
```

**Fix:**
```
> Prompt: "Replace project_enterprise with CE alternative."
> "Use odoo.addons.project instead."
> "Ensure __manifest__.py depends only on CE modules."
```

**Validation:**
```bash
grep -r "enterprise\|OEEL" addons/ipai_*/
```

---

### "Tests Failing After Scaffold"

**Symptom:**
```
psycopg2.errors.UndefinedTable: relation "ipai_equipment_equipment" does not exist
```

**Fix:**
```
> Paste exact error to AI
> Prompt: "Fix model name mismatch. Show only changed files."
> AI updates: models/__init__.py imports
```

---

### "Module Won't Install"

**Symptom:**
```
ParseError: Invalid XML
```

**Fix:**
```bash
# Validate XML
xmllint --noout addons/ipai_equipment/views/*.xml

# Paste validation errors to AI
> "Fix XML syntax errors in views/equipment_views.xml"
```

---

## 📊 Success Metrics

**After 3 months of vibe coding:**

| Metric | Baseline | Target | Current |
|--------|----------|--------|---------|
| Modules deployed | 3 | 10 | - |
| SaaS products replicated | 1 | 3 | - |
| Feature coverage | 60% | 90% | - |
| Deployment time | 2 days | 4 hours | - |
| Test coverage | 50% | 80% | - |
| Agent automation rate | 20% | 70% | - |

---

## 🚀 Next Steps

1. **Try it:**
   - Pick a small module/feature
   - Use Template 1 or 2
   - Complete full vibe coding workflow
   - Document learnings

2. **Automate it:**
   - Identify recurring patterns
   - Add to `AGENT_SKILLS_REGISTRY.yaml`
   - Create agent capability
   - Update reverse mapper

3. **Scale it:**
   - Deploy 3+ SaaS parity modules
   - Build Vibe Studio (spec in progress)
   - Train team on vibe coding
   - Measure productivity gains

---

## 📚 References

- **Agent Framework:** `agents/README.md`, `agents/ORCHESTRATOR.md`
- **Reverse Mapper:** `agents/odoo_reverse_mapper.yaml`
- **OCA Guidelines:** https://github.com/OCA/odoo-community.org
- **Odoo 18 Docs:** https://www.odoo.com/documentation/18.0/
- **Module Examples:** `addons/ipai_expense/`, `addons/ipai_equipment/`

---

**Version:** 1.0.0
**Created:** 2025-11-23
**Status:** Active
**Next Review:** 2025-12-07

---

🤖 **Ready to vibe code. Let's build InsightPulse into the ultimate SaaS replication engine.**
