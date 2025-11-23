-- ============================================================================
-- Claude Memory Database Schema
-- ============================================================================
-- Purpose: Local SQLite database for Claude Code agent memory
-- Replaces: Giant CLAUDE.md files with queryable, auto-updated memory
-- Integration: MCP server exposes this to Claude Code CLI
-- ============================================================================

-- High-level sections (policies, stack description, etc.)
CREATE TABLE IF NOT EXISTS sections (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT UNIQUE NOT NULL,      -- e.g. 'global_policies', 'odoo_ce_18_stack'
  title TEXT NOT NULL,
  markdown TEXT NOT NULL,
  updated_at TEXT DEFAULT (datetime('now'))
);

-- Create index for faster key lookups
CREATE INDEX IF NOT EXISTS idx_sections_key ON sections(key);

-- Repo / stack "facts" (key/value pairs)
CREATE TABLE IF NOT EXISTS facts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  namespace TEXT NOT NULL,       -- e.g. 'odoo', 'ipai', 'ci'
  key TEXT NOT NULL,
  value TEXT NOT NULL,
  updated_at TEXT DEFAULT (datetime('now')),
  UNIQUE(namespace, key)
);

-- Create index for faster namespace lookups
CREATE INDEX IF NOT EXISTS idx_facts_namespace ON facts(namespace);

-- Per directory / file memory
CREATE TABLE IF NOT EXISTS file_notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  path TEXT NOT NULL UNIQUE,     -- 'addons/ipai_expense/__init__.py'
  summary TEXT,                  -- 1-2 paragraph description
  tags TEXT,                     -- comma-separated tags
  last_commit TEXT,              -- git commit hash
  updated_at TEXT DEFAULT (datetime('now'))
);

-- Create index for faster path lookups
CREATE INDEX IF NOT EXISTS idx_file_notes_path ON file_notes(path);

-- Commit-level memory
CREATE TABLE IF NOT EXISTS commits (
  sha TEXT PRIMARY KEY,
  author TEXT,
  date TEXT,
  title TEXT,
  summary TEXT,                  -- short, machine-readable summary
  impact TEXT,                   -- e.g. 'odoo_ce_schema', 'ipai_module_api'
  created_at TEXT DEFAULT (datetime('now'))
);

-- Create index for faster date-based queries
CREATE INDEX IF NOT EXISTS idx_commits_date ON commits(date DESC);

-- ============================================================================
-- Seed Data: Global Policies
-- ============================================================================
INSERT OR REPLACE INTO sections (key, title, markdown) VALUES
('global_policies', 'Global Policies',
'# Global Policies

## CE/OCA-Only Policy
- **NEVER** use Odoo Enterprise modules
- **ALWAYS** prefer Odoo CE + OCA community modules
- **NO** odoo.com links in user-facing code
- **NO** IAP (In-App Purchase) dependencies

## Code Quality
- Follow OCA coding guidelines
- Add security/ir.model.access.csv for all models
- Use AGPL-3 license for custom modules
- Minimum 80% test coverage for new modules

## OCR Quality Standards
- Target: ≥85% success rate
- P95 latency: <30 seconds
- Field accuracy: ≥90% for date, total, vendor, currency
- Add normalization rules in adapter, not Odoo

## Deployment Standards
- Use M1 one-shot script for fresh deployments
- Always run CI checks before deploying
- Backup database before major upgrades
- Use Let''s Encrypt for SSL certificates
- Monitor service health endpoints

## Security
- Always enable RLS on Supabase tables
- Use X-API-KEY authentication for external APIs
- Implement rate limiting (e.g., 100 req/hour)
- Never commit secrets to git
- Use HTTPS/TLS for all endpoints
');

-- ============================================================================
-- Seed Data: Stack Configuration
-- ============================================================================
INSERT OR REPLACE INTO sections (key, title, markdown) VALUES
('odoo_ce_18_stack', 'Odoo CE 18 Stack Configuration',
'# Odoo CE 18 Stack

## Production Services

### Odoo CE 18
- **URL:** https://erp.insightpulseai.net
- **Version:** 18.0 CE
- **Deployment:** Docker Compose on DigitalOcean SGP1
- **Droplet:** odoo-erp-prod (4GB RAM, 80GB disk)
- **IP:** 159.223.75.148

### PostgreSQL
- **Container:** odoo-db (Postgres 16)
- **Database:** odoo
- **User:** odoo

### Supabase
- **Project ID:** spdtwktxdalcfigzeqrz
- **Region:** us-east-1
- **URL:** https://spdtwktxdalcfigzeqrz.supabase.co

### OCR Service
- **URL:** https://ocr.insightpulseai.net
- **Backend:** PaddleOCR-VL-900M
- **LLM:** OpenAI GPT-4o-mini
- **Droplet:** ocr-service-droplet (8GB RAM, 80GB disk)
- **IP:** 188.166.237.231

### n8n Automation
- **URL:** https://n8n.insightpulseai.net
- **Workspace:** fin-workspace
- **IP:** 159.223.75.148

### Superset Analytics
- **URL:** https://superset.insightpulseai.net
- **Deployment:** DigitalOcean App Platform

### MCP Coordinator
- **URL:** https://mcp.insightpulseai.net
- **Deployment:** DigitalOcean App Platform (pulse-hub-web-an645)

## IPAI Custom Modules (10)
1. ipai_cash_advance
2. ipai_ce_cleaner
3. ipai_docs
4. ipai_docs_project
5. ipai_equipment
6. ipai_expense
7. ipai_finance_monthly_closing
8. ipai_finance_ppm
9. ipai_ocr_expense
10. ipai_ppm_monthly_close
');

-- ============================================================================
-- Seed Data: Key Facts
-- ============================================================================
INSERT OR REPLACE INTO facts (namespace, key, value) VALUES
('odoo', 'version', '18.0 CE'),
('odoo', 'url', 'https://erp.insightpulseai.net'),
('odoo', 'deployment', 'Docker Compose + DigitalOcean'),
('supabase', 'project_id', 'spdtwktxdalcfigzeqrz'),
('supabase', 'region', 'us-east-1'),
('n8n', 'url', 'https://n8n.insightpulseai.net'),
('n8n', 'workspace', 'fin-workspace'),
('ocr', 'url', 'https://ocr.insightpulseai.net'),
('ocr', 'backend', 'PaddleOCR-VL-900M'),
('ocr', 'llm', 'OpenAI GPT-4o-mini'),
('mcp', 'coordinator_url', 'https://mcp.insightpulseai.net'),
('superset', 'url', 'https://superset.insightpulseai.net'),
('ci', 'workflow', '.github/workflows/odoo-parity-tests.yml'),
('ci', 'checks', 'CE/OCA compliance, no Enterprise deps, no odoo.com links');

-- ============================================================================
-- Seed Data: Module Notes
-- ============================================================================
INSERT OR REPLACE INTO file_notes (path, summary, tags) VALUES
('addons/ipai_expense', 'SAP Concur-style expense management with OCR integration', 'expense,concur-parity,ocr'),
('addons/ipai_equipment', 'Cheqroom-style equipment booking and management', 'equipment,cheqroom-parity,booking'),
('addons/ipai_docs', 'Notion-style document management', 'docs,notion-parity,workspace'),
('addons/ipai_finance_ppm', 'Finance PPM dashboard with ECharts visualizations', 'finance,ppm,dashboard'),
('addons/ipai_ocr_expense', 'OCR integration for expense receipt processing', 'ocr,expense,ml'),
('addons/ipai_cash_advance', 'Cash advance request and settlement workflow', 'expense,cash-advance,approval'),
('addons/ipai_finance_monthly_closing', 'Monthly finance closing task management', 'finance,closing,automation'),
('addons/ipai_ce_cleaner', 'Removes Enterprise branding and odoo.com links', 'ce,cleaner,branding'),
('addons/ipai_docs_project', 'Links documents to projects (Notion workspace integration)', 'docs,project,workspace'),
('addons/ipai_ppm_monthly_close', 'PPM monthly close automation integration', 'ppm,closing,automation');
