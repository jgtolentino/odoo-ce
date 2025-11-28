# InsightPulse ERP Target Image PRD

## Overview

This document defines the production target image specification for InsightPulse ERP based on Odoo 18 CE + OCA.

## Image Specification

| Property | Value |
|----------|-------|
| **Image Name** | `ghcr.io/jgtolentino/odoo-ce:18-oca-target` |
| **Base** | `odoo:18.0` |
| **Philosophy** | Smart Delta: Config -> OCA -> Delta -> Custom |
| **Database** | PostgreSQL 16 |

## Canonical 5-Module Architecture

| # | Module | Purpose | Status |
|---|--------|---------|--------|
| 1 | `ipai_dev_studio_base` | Foundation - aggregates CE/OCA deps, disables IAP | Core |
| 2 | `ipai_workspace_core` | Notion-style workspace foundation | Core |
| 3 | `ipai_ce_branding` | CE/OCA branding, hides Enterprise upsells | Core |
| 4 | `ipai_finance_ppm` | Accounting industry pack (BIR compliance) | Industry |
| 5 | `ipai_industry_marketing_agency` | Marketing agency industry pack | Industry |

## Directory Structure

```text
odoo-ce/
├── Dockerfile                    # Builds target image
├── docker-compose.yml            # Orchestrates db + app
├── config/
│   └── odoo.conf                 # Runtime configuration
├── ipai_addons/                  # EXACTLY 5 custom modules
│   ├── ipai_dev_studio_base/
│   ├── ipai_workspace_core/
│   ├── ipai_ce_branding/
│   ├── ipai_finance_ppm/
│   └── ipai_industry_marketing_agency/
├── oca_addons/                   # Vendored OCA repos
│   ├── web/
│   ├── server-tools/
│   ├── account-financial-reporting/
│   └── ...
└── docs/
    ├── PRD_TARGET_IMAGE.md
    ├── SMART_DELTA_PHILOSOPHY.md
    └── TROUBLESHOOTING_SMART_DELTA.md
```

## OCA Repositories Included

| Repository | Purpose |
|------------|---------|
| `web` | Web UX enhancements |
| `server-tools` | Server utilities |
| `reporting-engine` | Report generation |
| `account-closing` | Period closing |
| `account-financial-reporting` | Financial reports |
| `account-financial-tools` | Accounting utilities |
| `account-invoicing` | Invoice enhancements |
| `project` | Project management |
| `hr-expense` | Expense management |
| `purchase-workflow` | Purchase enhancements |
| `maintenance` | Maintenance management |
| `dms` | Document management |
| `calendar` | Calendar enhancements |
| `contract` | Contract management |

## Build & Deploy

### Build Image

```bash
docker build -t ghcr.io/jgtolentino/odoo-ce:18-oca-target .
```

### First-Run Initialization

```bash
docker compose run --rm odoo odoo -d ipai_prod \
  -i ipai_dev_studio_base,ipai_ce_branding,ipai_workspace_core,ipai_finance_ppm \
  --without-demo=all --load-language=en_US
```

### Start Stack

```bash
docker compose up -d
```

## Configuration

### Database Filter

Only databases matching `^(ipai_.*|odoo|insightpulse)$` are visible.

### Resource Limits

| Parameter | Value |
|-----------|-------|
| `limit_time_cpu` | 600 |
| `limit_time_real` | 1200 |
| `limit_memory_soft` | 2.5 GiB |
| `limit_memory_hard` | 3.0 GiB |

## Agent Contract

All AI agents working on this codebase must:

1. Assume `ipai_dev_studio_base` is installed
2. Never re-implement what CE/OCA already provides
3. Follow: Config -> OCA -> Delta -> Custom
4. Never suggest Enterprise or IAP features
