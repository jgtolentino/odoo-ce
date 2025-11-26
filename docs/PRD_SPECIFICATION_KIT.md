# Enterprise Platform Enablement — Unified Marketing, Finance, Delivery & Governance System

**Program Code:** P-OPS-ERP-2025-Q1
**Owner:** PMO / Systems Architecture
**Revision:** v1.0.0
**Status:** Approved for Build
**Platform:** Odoo CE 18.0 + OCA + n8n
**Target:** Marketing Agency Industry with Finance SSC Compliance

---

## 1. Purpose

This Specification Kit consolidates product, compliance, and configuration requirements for the deployment of an **Integrated Operations Platform** replacing:

- ❌ Salesforce CRM → ✅ Odoo CE CRM
- ❌ SAP Concur / Ariba SRM → ✅ Odoo CE + OCA Contract
- ❌ Clarity PPM → ✅ Odoo CE Project + OCA web_timeline
- ❌ Cheqroom → ✅ Odoo CE + OCA Maintenance
- ❌ Toggl / Harvest → ✅ Odoo CE hr_timesheet
- ❌ Hootsuite / Marketo → ✅ n8n + Odoo mass_mailing

**Target stack:** Odoo CE 18.0 + 14 OCA repositories + n8n automation + Keycloak SSO

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   FIN-WORKSPACE STACK                        │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: Custom Delta (2 modules only)                     │
│    └── ipai_bir_compliance, ipai_portal_fix                 │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: OCA Modules (14 repositories)                     │
│    └── contract, web_timeline, reporting-engine, etc.       │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: Odoo CE 18.0 Native Apps                          │
│    └── CRM, Sales, Project, Finance, HR, Website            │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Infrastructure                                    │
│    └── PostgreSQL 16, Nginx, Keycloak, n8n, Superset        │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Infrastructure & DNS Routing

### 3.1 Production Droplets

| Droplet | IP | Services |
|---------|-----|----------|
| `odoo-erp-prod` | 159.223.75.148 | Odoo, n8n, Mattermost, Keycloak |
| `ocr-service-droplet` | 188.166.237.231 | OCR API (PaddleOCR-VL) |

### 3.2 DNS Mapping (Authoritative)

| Host | Type | Target | Backend Location |
|------|------|--------|------------------|
| `insightpulseai.net` | A | 159.223.75.148 | Nginx on odoo-erp-prod |
| `www.insightpulseai.net` | CNAME | insightpulseai.net | Nginx on odoo-erp-prod |
| `erp.insightpulseai.net` | A | 159.223.75.148 | Odoo on odoo-erp-prod |
| `chat.insightpulseai.net` | A | 159.223.75.148 | Mattermost |
| `n8n.insightpulseai.net` | A | 159.223.75.148 | n8n orchestrator |
| `auth.insightpulseai.net` | A | 159.223.75.148 | Keycloak / Auth |
| `ocr.insightpulseai.net` | A | 188.166.237.231 | OCR service droplet |
| `superset.insightpulseai.net` | CNAME | superset-nlavf.ondigitalocean.app | DO App (Superset) |
| `mcp.insightpulseai.net` | CNAME | pulse-hub-web-an645.ondigitalocean.app | DO App (MCP Coord) |
| `agent.insightpulseai.net` | CNAME | wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run | DO Agent Service |

**CAA Record:** `0 issue "letsencrypt.org"` (Let's Encrypt only)

### 3.3 Nginx Configuration

See `infra/nginx/erp-droplet/fin-workspace.nginx.conf` for complete reverse proxy configuration.

**Key upstream mappings:**
- Odoo: `127.0.0.1:8069`
- Mattermost: `127.0.0.1:8065`
- n8n: `127.0.0.1:5678`
- Keycloak: `127.0.0.1:8080`

---

## 4. Scope

### 4.1 Included

| Domain | Scope Type | Notes |
|--------|------------|-------|
| CRM & Opportunity Lifecycle | Full | Replace Salesforce Sales Cloud |
| Retainer & Contract Billing | Full | OCA contract (superior to Ariba SRM) |
| PMO & Delivery Governance | Full | Clarity PPM functional equivalence |
| Timesheets + Expense & Cost Control | Full | SAP Concur + Harvest equivalence |
| Asset Registry | Partial | Cheqroom parity baseline, QR tracking |
| Campaign + Marketing Ops | Partial | Workflow-driven via n8n |
| BIR Compliance (Philippines) | Full | Monthly/quarterly tax filing automation |

### 4.2 Excluded

| Item | Reason |
|------|--------|
| Built-in AI content generation | External agent orchestration via n8n |
| Native social posting UI | Use n8n automation with platform APIs |
| Odoo Enterprise modules | 95%+ parity achieved with CE + OCA |

---

## 5. Business Requirements

| Requirement Category | ID | Requirement | Compliance Target |
|---------------------|-----|-------------|------------------|
| Opportunity Governance | BR-001 | All leads progress through controlled sales motion with SLA tracking | 100% |
| Retainer Billing | BR-019 | Contract billing must enforce pre-approved work scope and renewal cadence | 100% |
| Project Delivery Governance | BR-032 | PMO must manage milestones, dependencies, resource plans and burndown metrics | ≥95% |
| Financial Controls | BR-057 | Expenses, cost centers, and approval matrix must reflect policy lineage | 100% |
| Audit & Traceability | BR-092 | Every workflow change must be timestamped and attributable | 100% |
| BIR Compliance | BR-093 | Automated BIR 2307 + DAT file generation with 100% accuracy | 100% |

---

## 6. Functional Requirements

### 6.1 CRM (Lead Management)

| Feature | Enterprise | CE + OCA 18.0 | Status |
|---------|-----------|---------------|--------|
| Pipeline management | ✅ Native | ✅ Native crm | ✅ |
| Lead scoring | ✅ Predictive AI | ⚠️ Manual rules | 80% |
| Email integration | ✅ Native | ✅ Native | ✅ |
| WhatsApp integration | ✅ Native | 🔧 n8n webhook | 90% |
| Activity scheduling | ✅ Native | ✅ Native | ✅ |
| Reporting/Dashboard | ✅ Native | ✅ Native + bi_sql_editor | ✅ |

### 6.2 Subscriptions / Retainers ⭐

| Feature | Enterprise | CE + OCA 18.0 | Status |
|---------|-----------|---------------|--------|
| Recurring billing | ✅ subscription | ✅ OCA contract | ✅ Better |
| Use-it-or-lose-it hours | ❌ Not native | ✅ OCA contract | ✅ Better |
| Auto-renewal | ✅ Native | ✅ OCA contract | ✅ |
| Retainer tracking | ⚠️ Basic | ✅ OCA contract_sale | ✅ |

**Note:** OCA contract is superior for agency retainers with complex hour pools.

### 6.3 Project Management

| Feature | Enterprise | CE + OCA 18.0 | Status |
|---------|-----------|---------------|--------|
| Task management | ✅ Native | ✅ Native project | ✅ |
| Kanban/List views | ✅ Native | ✅ Native | ✅ |
| Gantt view | ✅ Native | ✅ OCA web_timeline | ✅ |
| Milestones | ✅ Native | ✅ Native (v17+) | ✅ |
| Subtasks | ✅ Native | ✅ Native | ✅ |
| Dependencies | ✅ Native | ✅ Native | ✅ |
| Resource planning | ✅ planning | ✅ OCA project_timeline | 90% |
| Burndown charts | ✅ Native | 🔧 Metabase/Superset | 85% |

### 6.4 Finance & BIR Compliance

| Feature | Enterprise | CE + OCA 18.0 | Status |
|---------|-----------|---------------|--------|
| Invoicing | ✅ Native | ✅ Native account | ✅ |
| Expense management | ✅ Native | ✅ Native hr_expense | ✅ |
| Expense approval | ✅ Native | ✅ OCA hr_expense_advance | ✅ |
| Multi-currency | ✅ Native | ✅ Native | ✅ |
| BIR 2307 Generation | ❌ Not available | ✅ ipai_bir_compliance | ✅ Custom |
| BIR DAT Export | ❌ Not available | ✅ ipai_bir_compliance | ✅ Custom |
| Monthly Tax Filing Tracker | ❌ Not available | ✅ n8n + Odoo Project | ✅ Automation |

---

## 7. Technical Architecture

### 7.1 System Architecture

```yaml
system_architecture:
  platform: "Odoo CE + OCA v18.0"
  integration_bus: "n8n (event orchestration + policy routing)"
  reporting_stack: "Superset + PostgreSQL + dbt governance"
  IAM:
    - SSO SAML2 (Keycloak)
    - Role-based segregation
    - Audit authority: Finance Ops, PMO, Information Security
  deployment:
    environment:
      - DEV
      - STAGE
      - PROD
    compliance:
      - change control via PR
      - migrations via Odoo migrations + SQL scripts
```

### 7.2 OCA Submodules (14 Repositories)

| Repository | Branch | Purpose |
|------------|--------|---------|
| reporting-engine | 18.0 | bi_sql_editor for dashboards |
| account-closing | 18.0 | Fiscal year closing |
| account-financial-reporting | 18.0 | GL, Trial Balance, Tax reports |
| account-financial-tools | 18.0 | Lock dates, asset management |
| account-invoicing | 18.0 | Withholding tax (EWT) |
| project | 18.0 | Milestones, timeline |
| hr-expense | 18.0 | Expense approval tiers |
| purchase-workflow | 18.0 | RFQ, purchase requests |
| maintenance | 18.0 | Asset tracking |
| dms | 18.0 | Document management |
| calendar | 18.0 | Resource booking |
| web | 18.0 | web_timeline (Gantt) |
| contract | 18.0 | Supplier agreements, retainers |
| server-tools | 18.0 | Automation utilities |

### 7.3 Custom Delta Modules (2 Only)

| Module | Purpose | Dependencies |
|--------|---------|--------------|
| `ipai_bir_compliance` | BIR 2307 + DAT file generator, PH tax compliance | account |
| `ipai_portal_fix` | Fix KeyError: 'website' in portal templates | portal |

**Deprecated Modules (Removed):**
- ❌ `tbwa_spectra_integration` - Use native CSV/Excel export
- ❌ `ipai_docs*` - Use native Knowledge app
- ❌ `ipai_ce_cleaner` - Not required for production

---

## 8. Data Governance

### 8.1 Classification Matrix

| Data Class | Examples | Storage | Encryption | Retention |
|------------|----------|---------|------------|-----------|
| Tier 1 — Regulated (Finance) | Billing, invoices, expenses, BIR forms | PostgreSQL 16 | AES-256 at rest | 7–10 years |
| Tier 2 — Operational Data | CRM, Projects, Tasks | PostgreSQL 16 | AES-256 | 5 years |
| Tier 3 — Marketing/Public | Website, portfolio, blog | Public repo cache | Optional | Unlimited |

### 8.2 Database Configuration

```yaml
postgresql_16:
  image: postgres:16-alpine
  environment:
    POSTGRES_DB: odoo
    POSTGRES_USER: odoo
    POSTGRES_PASSWORD: ${DB_PASSWORD}
  tuning:
    max_connections: 100
    shared_buffers: 256MB
    effective_cache_size: 1GB
    work_mem: 16MB
```

---

## 9. Compliance & Audit Controls

### 9.1 BIR Monthly Task Matrix

Based on `BIR_SCHEDULE_2026.xlsx`:

| BIR Form | Frequency | Records | Workflow Steps |
|----------|-----------|---------|----------------|
| 1601-C | Monthly | 12 | Prep → Review → Approval → Filing |
| 0619-E | Monthly | 12 | Prep → Review → Approval → Filing |
| 2550Q | Quarterly | 4 | Prep → Review → Approval → Filing |
| 1601-EQ | Quarterly | 4 | Prep → Review → Approval → Filing |
| 1702Q | Quarterly | 4 | Prep → Review → Approval → Filing |

**Total:** 36 BIR schedule records with automated task generation

### 9.2 Workflow Roles

| Role | Assignment | Odoo Group |
|------|------------|------------|
| Finance Supervisor | Preparation (Step 1) | Finance / User |
| Senior Finance Manager | Review (Step 2) | Finance / Manager |
| Finance Director | Approval (Step 3) | Finance / Director |

### 9.3 Monthly Close Process (IM1 + IM2)

**Logical Framework:**

```
Goal: 100% compliant and timely month-end closing and tax filing

Outcome: Zero-penalty compliance with timely financial reporting

IM1: Month-End Closing
  └── Outputs: Reconciliations, Journal Entries
      └── Activities: Bank/GL Recon, Accruals, WIP

IM2: Tax Filing
  └── Outputs: BIR Forms Filed
      └── Activities: WHT Computation, VAT Computation
```

**Implementation:**
- No custom modules required
- Use Odoo CE Project + Tasks + Stages
- n8n automation generates tasks from BIR schedule
- Evidence stored as task attachments (PDF exports from Odoo reports)

---

## 10. n8n Automation Workflows

### 10.1 BIR Task Generator Workflow

```yaml
trigger: Scheduled (daily at 01:00 UTC+8)
data_source: Google Sheet (BIR_SCHEDULE_2026.xlsx)
logic:
  - Read sheet rows (BIR forms + periods + deadlines)
  - For each row:
      - Generate unique key: form_code + period + year
      - Create 4 tasks in Odoo Project:
          1. [Form] [Period] – Preparation (Finance Supervisor)
          2. [Form] [Period] – Report Approval (Senior Finance Manager)
          3. [Form] [Period] – Payment Approval (Finance Director)
          4. [Form] [Period] – Filing & Payment (Finance Supervisor)
      - Set deadlines from sheet columns
      - Tag with: BIR form code, period, IM2-Tax
  - Send Mattermost alert if deadline ≤ 7 days
```

### 10.2 OCR Expense Webhook

```yaml
trigger: OCR service completes processing (POST /webhook/ocr-complete)
logic:
  - If confidence ≥ 60%:
      - Create Odoo expense via API
      - Mattermost: "#expenses - Auto-created expense #{id}"
  - If confidence < 60%:
      - Create review task in Odoo
      - Mattermost: "#expenses - Manual review required: {receipt_url}"
```

### 10.3 Contact Enrichment Agent

```yaml
trigger: Odoo creates new contact (POST /webhook/enrich-contact)
logic:
  - Extract email domain
  - GPT-4o-mini: Determine industry + summary
  - Search for tag in Odoo (res.partner.category)
  - If not exists: Create tag
  - Update contact with tag + AI summary in comment field
```

---

## 11. UI/UX Specification

### 11.1 Portal Fix Requirements

| Criterion | Requirement |
|-----------|-------------|
| Accessibility | WCAG AA |
| Component Model | Odoo OWL + reusable blocks |
| Interaction Standard | One-click rule for dominant actions |
| Cross-platform | OWL → React/Vue/Next.js adapters |

**Module:** `ipai_portal_fix`
- Fixes `KeyError: 'website'` in portal templates
- Injects safe default for `website` variable
- TBWA/OMC branding personalization

---

## 12. Implementation Governance

| Governance Layer | Owner | Cadence |
|------------------|-------|---------|
| Steering Committee | CIO + CFO + PMO | Monthly |
| Change Advisory Board | DevOps + PMO + Compliance | Weekly |
| Operational Runbook | Finance Ops + IT | Daily |

---

## 13. Acceptance Exit Criteria

Must satisfy:

- ✅ 95%+ feature parity to target enterprise systems
- ✅ All workflows mapped and documented
- ✅ Data migration validation complete
- ✅ Audit controls tested and logged
- ✅ User adoption baseline ≥ 80%
- ✅ SLA performance validated
- ✅ BIR filing accuracy ≥ 98%
- ✅ Visual parity: SSIM ≥ 0.97 (mobile), ≥ 0.98 (desktop)

---

## 14. Build & Deploy Commands

### 14.1 Build Production Image

```bash
# Build delta image FROM stable base
docker build -f Dockerfile.delta -t ghcr.io/jgtolentino/odoo-ce:marketing-latest .

# Export to tar
docker save ghcr.io/jgtolentino/odoo-ce:marketing-latest | gzip > odoo-marketing-v1.tar.gz

# Transfer to server
scp odoo-marketing-v1.tar.gz ubuntu@159.223.75.148:/opt/odoo/

# Load on server
ssh ubuntu@159.223.75.148
cd /opt/odoo
gunzip -c odoo-marketing-v1.tar.gz | docker load

# Deploy
docker compose -f docker-compose.prod.yml up -d
```

### 14.2 Initialize Database

```bash
# Install core modules
docker exec odoo-ce odoo -d odoo -i \
  base,mail,contacts,account,sale,crm,project,hr,hr_timesheet,hr_expense,website,website_blog \
  --stop-after-init

# Install custom modules
docker exec odoo-ce odoo -d odoo -i \
  ipai_bir_compliance,ipai_portal_fix \
  --stop-after-init
```

---

## 15. Coverage Summary

| Category | Coverage |
|----------|----------|
| CRM | 100% |
| Sales | 100% |
| Subscriptions/Retainers | 100% (OCA better) |
| Project | 95% |
| Timesheets | 100% |
| Website | 90% (no AI builder) |
| Social Marketing | 85% (n8n required) |
| Marketing Automation | 90% |
| Events | 95% |
| Invoicing | 100% |
| BIR Compliance | 100% |
| **Overall** | **95%+** |

---

## 16. Repository Structure

```
fin-workspace/
├── docs/
│   ├── PRD_SPECIFICATION_KIT.md (this file)
│   ├── ARCHITECTURE/
│   │   └── FIN_WORKSPACE_SYSTEM.md
│   ├── COMPLIANCE/
│   │   └── controls/
│   └── RUNBOOK/
│       └── NGINX_ROUTING.md
├── infra/
│   ├── nginx/
│   │   ├── erp-droplet/
│   │   │   └── fin-workspace.nginx.conf
│   │   └── ocr-droplet/
│   │       └── ocr-service.nginx.conf
│   └── scripts/
│       └── reload-nginx.sh
├── Dockerfile.delta
├── deploy/
│   ├── docker-compose.prod.yml
│   └── odoo.conf
└── addons/
    ├── ipai_bir_compliance/
    └── ipai_portal_fix/
```

---

## 17. References

- [Odoo Marketing Agency Package](https://www.odoo.com/industries/marketing-agency)
- [Odoo 18 Finance Documentation](https://www.odoo.com/documentation/18.0/applications/finance.html)
- [BIR eBIRForms](https://www.bir.gov.ph/ebirforms)
- [OCA Project Homepage](https://github.com/OCA)

---

**Last Updated:** 2025-11-26
**Version:** 1.0.0
**Approved By:** Finance SSC + PMO
**Next Review:** 2026-01-15
