# Odoo CE 18.0 - Unified Changelog

All notable changes to the Odoo CE Docker image and Finance PPM system.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Finance PPM Module
- **ipai_finance_ppm** - Complete Finance Project Portfolio Management system
- Logical Framework (Logframe) tracking with Goal → Outcome → IM1/IM2 → Outputs → Activities
- BIR tax filing calendar with 8 form types (1601-C, 0619-E, 2550Q, etc.)
- ECharts dashboard at `/ipai/finance/ppm`
- Automated task creation cron (daily at 8AM)
- Integration with n8n workflows and Mattermost notifications

### 🔧 Fixed

#### Production HTTPS Fix: Mixed Content Asset Loading (2025-11-26)
- **Issue**: Mixed Content errors causing broken CSS/JS on production HTTPS site
- **Root Cause**: `web.base.url` not set to HTTPS in database
- **Impact**: CRITICAL - Login page displayed without styling
- **Fix**:
  - Set `web.base.url = https://erp.insightpulseai.net` in `ir_config_parameter`
  - Added `web.base.url.freeze = True`
  - Cleared cached HTTP asset bundles
- **Documentation**: See `docs/MIXED_CONTENT_FIX.md`

---

## [1.2.0] - 2025-11-24 — Monitoring & BI Integration

### Added
- **Monitoring Schema** (`deploy/monitoring_schema.sql`)
  - `monitoring.service_health_checks` - Service uptime and latency tracking
  - `monitoring.backup_verifications` - Backup success/failure tracking
  - Optimized indexes for time-series queries

- **Superset-Ready Views** (`deploy/monitoring_views.sql`)
  - `monitoring.v_service_uptime_daily` - Daily uptime percentage
  - `monitoring.v_backup_status_daily` - Daily backup success rates

- **n8n Integration Ready**
  - Healthcheck and backup scripts with n8n webhook support
  - JSON payload format optimized for n8n workflow ingestion

---

## [1.1.0] - 2025-11-24 — Production Readiness Bundle

### Added
- **Database & Worker Tuning** (`docs/DB_TUNING.md`)
  - PostgreSQL connection limit: 100
  - Odoo worker configuration: 4 HTTP workers, 2 cron workers

- **Installation Safety**
  - `scripts/pre_install_snapshot.sh` - Pre-install database backups
  - `scripts/install_ipai_finance_ppm.sh` - Safe module installation wrapper

- **Documentation & Procedures**
  - `docs/N8N_CREDENTIALS_BOOTSTRAP.md`
  - `docs/MATTERMOST_ALERTING_SETUP.md`
  - `docs/APP_ICONS_README.md`

- **Regression Test Scaffolding**
  - Complete test suite for `ipai_equipment`, `ipai_expense`, `ipai_finance_ppm`

---

## [v0.9.1] - 2025-11-25

### 🔒 Security & Compliance Release

### ✅ Fixed

#### Critical Fix #1: Python Requirements Installation
- **Fix**: Automatic installation of Python dependencies from `requirements.txt`
- **Impact**: HIGH - Prevents module loading failures

#### Critical Fix #2: Environment Variable Defaults
- **Fix**: Added default ENV vars for database connection
- **Impact**: HIGH - Kubernetes compatibility, 12-factor app compliance

#### Critical Fix #3: Health Check Configuration
- **Fix**: Added HEALTHCHECK directive
- **Impact**: HIGH - Docker/Kubernetes orchestration support

### 📦 Added

#### Deployment Automation
- **scripts/build_v0.9.1.sh**: Automated build and push script
- **scripts/deploy_prod.sh**: Production deployment script
- **scripts/smoketest.sh**: Comprehensive smoke test suite (40+ tests)

---

## Production Deployment Notes

### Docker Image
- Base: `odoo:18.0`
- 14 OCA repositories
- 5 custom modules: Finance PPM, Tax Shield, CE Cleaner, Portal Fix, Spectra
- PostgreSQL 16 client for Supabase compatibility
- Health checks enabled

### Environment Requirements
- PostgreSQL 16 (Supabase pooler port 6543)
- Keycloak SSO for erp.insightpulseai.net
- n8n workflows for automation
- Mattermost for notifications
- Apache Superset for BI dashboards
